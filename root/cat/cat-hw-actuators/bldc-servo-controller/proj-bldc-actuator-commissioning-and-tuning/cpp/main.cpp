#include "bldc_calibrator.hpp"

#include <iostream>
#include <iomanip>
#include <cmath>

namespace {

/**
 * @brief Модель апаратного інвертора та фізики безколекторного двигуна з навантаженням.
 * Імітує реакцію ротора на фазові струми та розрахунок електромеханічного моменту.
 */
class SimulatedMotorInverter : public bldc_servo::IInverter {
public:
    SimulatedMotorInverter(float physical_zero_offset_rad, uint16_t pole_pairs = 7)
        : physical_zero_offset_(physical_zero_offset_rad), pole_pairs_(pole_pairs) {}

    void enable() noexcept override {
        is_enabled_ = true;
    }

    void disable() noexcept override {
        is_enabled_ = false;
        id_cmd_ = 0.0f;
        iq_cmd_ = 0.0f;
    }

    void apply_id_vector(float id_amps) noexcept override {
        id_cmd_ = id_amps;
        iq_cmd_ = 0.0f;
    }

    void apply_torque_current(float iq_amps, float electrical_angle_rad) noexcept override {
        id_cmd_ = 0.0f;
        iq_cmd_ = iq_amps;
        stator_field_angle_rad_ = electrical_angle_rad;
    }

    bool is_fault() const noexcept override {
        return has_fault_;
    }

    void set_fault(bool fault) noexcept {
        has_fault_ = fault;
    }

    /**
     * @brief Чисельне інтегрування диференціальних рівнянь руху ротора в реальному часі.
     * Модель: J * d^2(theta)/dt^2 + B * d(theta)/dt = T_motor
     */
    void update_physics(float dt_seconds) noexcept {
        if (dt_seconds <= 1e-6f) return;

        float motor_torque_nm = 0.0f;

        if (is_enabled_) {
            // Фактичний електричний кут ротора відносно статора
            const float rotor_elec_angle = (rotor_angle_rad_ - physical_zero_offset_) * static_cast<float>(pole_pairs_);

            if (std::abs(id_cmd_) > 0.001f) {
                // Статичний вектор Id створює повертальний синхронізуючий момент до найближчого нуля фази A
                motor_torque_nm = -align_stiffness_ * id_cmd_ * std::sin(rotor_elec_angle);
            } else {
                // Вектор Iq генерує момент за орієнтацією магнітного поля статора
                const float angle_err = stator_field_angle_rad_ - rotor_elec_angle;
                motor_torque_nm = motor_kt_ * iq_cmd_ * std::cos(angle_err);
            }
        }

        // Механічна динаміка другого порядку з в'язким тертям
        const float damping_torque = viscous_damping_ * rotor_velocity_rad_s_;
        const float net_torque = motor_torque_nm - damping_torque;
        const float angular_acceleration = net_torque / total_inertia_;

        rotor_velocity_rad_s_ += angular_acceleration * dt_seconds;
        rotor_angle_rad_ += rotor_velocity_rad_s_ * dt_seconds;
    }

    [[nodiscard]] float rotor_angle_rad() const noexcept { return rotor_angle_rad_; }
    [[nodiscard]] float rotor_velocity_rad_s() const noexcept { return rotor_velocity_rad_s_; }

private:
    float physical_zero_offset_{1.2566f}; // Фізичне кутове зміщення нуля енкодера (близько 72 градусів)
    uint16_t pole_pairs_{7};

    bool is_enabled_{false};
    bool has_fault_{false};
    float id_cmd_{0.0f};
    float iq_cmd_{0.0f};
    float stator_field_angle_rad_{0.0f};

    // Фізичні параметри приводного вузла
    float rotor_angle_rad_{0.10f};            // Початкове довільне механічне положення
    float rotor_velocity_rad_s_{0.0f};
    float total_inertia_{0.00045f};           // кг * м^2
    float viscous_damping_{0.008f};           // Н * м * с / рад
    float motor_kt_{0.08f};                   // Н * м / А
    float align_stiffness_{0.35f};            // Відновлювальна жорсткість при вирівнюванні Id
};

/**
 * @brief Модель магнітного абсолютного енкодера високої роздільної здатності (14 біт).
 */
class SimulatedEncoder : public bldc_servo::IEncoder {
public:
    explicit SimulatedEncoder(const SimulatedMotorInverter& motor, uint32_t cpr = 16384)
        : motor_(motor), cpr_(cpr) {}

    uint32_t read_raw_ticks() const noexcept override {
        const float angle = read_mechanical_angle_rad();
        constexpr float two_pi = 2.0f * 3.14159265358979323846f;
        const float norm = std::fmod(angle, two_pi);
        const float pos = (norm < 0.0f) ? norm + two_pi : norm;
        return static_cast<uint32_t>((pos / two_pi) * static_cast<float>(cpr_));
    }

    uint32_t counts_per_rev() const noexcept override {
        return cpr_;
    }

    float read_mechanical_angle_rad() const noexcept override {
        return motor_.rotor_angle_rad();
    }

    bool is_ready() const noexcept override {
        return is_ready_;
    }

    void set_ready(bool ready) noexcept { is_ready_ = ready; }

private:
    const SimulatedMotorInverter& motor_;
    uint32_t cpr_{16384};
    bool is_ready_{true};
};

/**
 * @brief Емуляція пам'яті EEPROM / Flash на базі внутрішнього статичного буфера в ОЗП.
 */
class SimulatedNVMemory : public bldc_servo::INVMemory {
public:
    static constexpr size_t kCapacity = 512;

    bool write(uint32_t address, const uint8_t* data, size_t size) noexcept override {
        if (address + size > kCapacity || data == nullptr) {
            return false;
        }
        for (size_t i = 0; i < size; ++i) {
            buffer_[address + i] = data[i];
        }
        return true;
    }

    bool read(uint32_t address, uint8_t* data, size_t size) const noexcept override {
        if (address + size > kCapacity || data == nullptr) {
            return false;
        }
        for (size_t i = 0; i < size; ++i) {
            data[i] = buffer_[address + i];
        }
        return true;
    }

    /** @brief Штучна інверсія біта для симуляції апаратного пошкодження пам'яті. */
    void corrupt_byte(uint32_t address) noexcept {
        if (address < kCapacity) {
            buffer_[address] ^= 0xFF;
        }
    }

private:
    std::array<uint8_t, kCapacity> buffer_{};
};

} // namespace

int main() {
    std::cout << "========================================================================\n"
              << "   BLDC Servo Controller: Автоналагодження та калібрування контурів   \n"
              << "========================================================================\n\n";

    // 1. Створення об'єктів апаратного рівня та емулятора фізики привода
    // Фізичне заводське зміщення нуля енкодера: 1.2566 рад (72.0 градуси)
    constexpr float kRealPhysicalOffsetRad = 1.2566f;
    constexpr uint16_t kPolePairs = 7;
    constexpr float kMotorKt = 0.08f; // Н*м / А

    SimulatedMotorInverter motor_inverter(kRealPhysicalOffsetRad, kPolePairs);
    SimulatedEncoder encoder(motor_inverter, 16384);
    SimulatedNVMemory eeprom;

    // 2. Ініціалізація підсистем керування
    bldc_servo::CalibrationStorage storage(eeprom, 0x0040); // Базовий сектор конфігурації
    bldc_servo::CascadeController controller;
    bldc_servo::BldcCalibrator calibrator(motor_inverter, encoder, controller, storage, kPolePairs, kMotorKt);

    std::cout << "[1] Початковий стан: Привод очікує калібрування.\n"
              << "    Справжнє фізичне зміщення енкодера: " << kRealPhysicalOffsetRad << " рад ("
              << (kRealPhysicalOffsetRad * 180.0f / 3.14159265f) << " град)\n\n";

    // 3. Запуск процедури калібрування: тестовий стрибок завдання на 1.0 рад
    calibrator.start_calibration(1.0f);

    bldc_servo::CalibrationState prev_state = bldc_servo::CalibrationState::Idle;

    // Симуляція диспетчера завдань реального часу з тактом 1 мс
    constexpr uint32_t kTotalSimulationMs = 1200;
    constexpr float kDtSec = 0.001f;

    for (uint32_t current_ms = 0; current_ms <= kTotalSimulationMs; ++current_ms) {
        // Оновлення фізики ротора двигуна під дією прикладених фазних струмів
        motor_inverter.update_physics(kDtSec);

        // Крок скінченного автомата автоналагодження
        calibrator.step(current_ms);

        // Фіксація та логування переходів між станами автомата
        const auto current_state = calibrator.state();
        if (current_state != prev_state) {
            std::cout << "  [t = " << std::setw(4) << current_ms << " мс] Зміна стану: "
                      << calibrator.state_name() << "\n";
            prev_state = current_state;

            if (current_state == bldc_servo::CalibrationState::TuningGains) {
                const float mech_pole_pitch = 2.0f * 3.14159265f / kPolePairs;
                const float diff = std::abs(calibrator.zero_offset_rad() - kRealPhysicalOffsetRad);
                const float elec_err = std::fmod(diff * kPolePairs, 2.0f * 3.14159265f);
                std::cout << "    >> Визначено електричний нуль енкодера: "
                          << calibrator.zero_offset_rad() << " рад (похибка електричного кута: "
                          << (elec_err < 1e-4f ? 0.0f : elec_err) << " рад, кратність полюсу: "
                          << std::round(diff / mech_pole_pitch) << ")\n";
            } else if (current_state == bldc_servo::CalibrationState::RunningStepTest) {
                const auto& gains = controller.gains();
                std::cout << "    >> Синтезовано каскадні коефіцієнти:\n"
                          << "       Pos Kp: " << gains.pos_kp << " 1/с, Pos Ki: " << gains.pos_ki << "\n"
                          << "       Vel Kp: " << gains.vel_kp << " А*с/рад, Vel Ki: " << gains.vel_ki << " А/рад\n";
            }
        }

        if (calibrator.is_completed() || calibrator.has_fault()) {
            break;
        }
    }

    std::cout << "\n[2] Результати верифікації якості автоналагодження:\n";
    if (calibrator.is_completed()) {
        const auto& metrics = calibrator.step_metrics();
        std::cout << "    Статус: УСПІШНО ЗАВЕРШЕНО\n"
                  << "    Час наростання (10%->90%):    " << metrics.rise_time_ms << " мс\n"
                  << "    Час заспокоєння (+-5%):       " << metrics.settling_time_ms << " мс\n"
                  << "    Перерегулювання:              " << std::fixed << std::setprecision(2)
                  << metrics.overshoot_percent << " %\n"
                  << "    Усталена статична похибка:    " << std::setprecision(4)
                  << metrics.steady_state_error_rad << " рад\n"
                  << "    Стійкість замкненого контуру: " << (metrics.is_stable ? "ГАРАНТОВАНО" : "НІ") << "\n";
    } else {
        std::cout << "    Статус: ВІДМОВА! Причина: " << calibrator.error_name() << "\n";
    }

    // 4. Перевірка цілісності даних у сховищі (EEPROM)
    std::cout << "\n[3] Верифікація збереженого зміщення нуля та CRC32 в EEPROM:\n";
    bldc_servo::CalibrationData loaded{};
    if (storage.load(loaded)) {
        std::cout << "    Сигнатура:       0x" << std::hex << loaded.magic << std::dec << "\n"
                  << "    Версія:          " << loaded.version << "\n"
                  << "    Пар полюсів:     " << loaded.pole_pairs << "\n"
                  << "    Зміщення нуля:   " << loaded.zero_offset_rad << " рад\n"
                  << "    Контрольна сума: 0x" << std::hex << loaded.crc32 << std::dec
                  << " [CRC32 ПІДТВЕРДЖЕНО]\n";
    } else {
        std::cout << "    ПОМИЛКА: Неможливо прочитати валідні калібрувальні дані!\n";
    }

    // Демонстрація реакції захисту на апаратне пошкодження біта в пам'яті
    std::cout << "\n[4] Тест стійкості: штучне пошкодження пам'яті (Bit-flip attack)...\n";
    eeprom.corrupt_byte(storage.base_address() + offsetof(bldc_servo::CalibrationData, zero_offset_rad));
    if (!storage.load(loaded)) {
        std::cout << "    Успіх захисту: Системою виявлено пошкодження CRC32! Аварійна розкалібровка відхилена.\n";
    }

    // 5. Виведення таблиці точок перехідного процесу
    std::cout << "\n[5] Масив телеметрії перехідної характеристики (перші 12 точок кроку):\n";
    std::cout << "   Час(мс) | Ціль(рад) | Факт(рад) | Похибка(рад) | Струм Iq(А)\n";
    std::cout << "  ---------+-----------+-----------+--------------+-------------\n";

    const auto& buffer = calibrator.telemetry_buffer();
    const size_t count = std::min<size_t>(calibrator.telemetry_count(), 12);
    for (size_t i = 0; i < count; ++i) {
        const auto& pt = buffer[i];
        std::cout << "   " << std::setw(6) << pt.timestamp_ms << "  |  "
                  << std::fixed << std::setprecision(3) << std::setw(7) << pt.target_pos_rad << "  |  "
                  << std::setw(7) << pt.actual_pos_rad << "  |  "
                  << std::setw(10) << (pt.target_pos_rad - pt.actual_pos_rad) << "  |  "
                  << std::setw(8) << pt.current_iq_amps << "\n";
    }

    std::cout << "\n[КІНЕЦЬ] Демонстрацію повного життєвого циклу пусконалагодження BLDC завершено.\n";
    return 0;
}
