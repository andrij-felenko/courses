#include "laser_output.hpp"
#include "strobe_controller.hpp"
#include "ambient_adaptor.hpp"
#include "thermal_guard.hpp"
#include "safety_supervisor.hpp"

#include <iostream>
#include <iomanip>
#include <chrono>
#include <thread>

/**
 * @brief Емуляція апаратного ШІМ-виходу мікроконтролера.
 */
class HardwarePwmMock : public laser::IPwmHardware {
public:
    void set_frequency_hz(uint32_t freq_hz) override {
        frequency_hz_ = freq_hz;
    }
    void set_duty_permille(uint16_t permille) override {
        duty_permille_ = permille;
    }
    void enable_output() override {
        is_active_ = true;
    }
    void disable_output() override {
        is_active_ = false;
    }
    void force_pin_low() override {
        is_active_ = false;
        duty_permille_ = 0;
    }

    [[nodiscard]] bool is_active() const noexcept { return is_active_; }
    [[nodiscard]] uint16_t duty() const noexcept { return duty_permille_; }

private:
    uint32_t frequency_hz_{25000};
    uint16_t duty_permille_{0};
    bool is_active_{false};
};

/**
 * @brief Емуляція апаратних датчиків безпеки (контур Interlock та АЦП напруги).
 */
class HardwareSafetyMock : public laser::ISafetyHardware {
public:
    bool read_interlock_closed() override {
        return interlock_closed_;
    }
    uint16_t read_voltage_mv() override {
        return voltage_mv_;
    }

    void set_interlock(bool closed) noexcept { interlock_closed_ = closed; }
    void set_voltage(uint16_t mv) noexcept { voltage_mv_ = mv; }

private:
    bool interlock_closed_{true};
    uint16_t voltage_mv_{5000}; // Номінальні 5.0 В
};

/**
 * @brief Допоміжний переклад помилки в текстовий вигляд для телеметрії.
 */
static const char* fault_to_string(laser::SafetyFault fault) {
    switch (fault) {
        case laser::SafetyFault::None:              return "НОРМА (No Fault)";
        case laser::SafetyFault::InterlockOpen:      return "РОЗРИВ ІНТЕРЛОКУ (Interlock Open)";
        case laser::SafetyFault::VoltageOutOfRange:  return "НЕПРИПУСТИМА НАПРУГА (Voltage Fault)";
        case laser::SafetyFault::ThermalShutdown:    return "ТЕПЛОВИЙ ПЕРЕГРІВ (Thermal Shutdown)";
        case laser::SafetyFault::WatchdogFault:       return "ВТРАТА ЗВ'ЯЗКУ (Watchdog Fault)";
        default:                                    return "НЕВІДОМО";
    }
}

/**
 * @brief Точка входу демонстраційного застосунку об'єктно-орієнтованої платформи лазера.
 */
int main() {
    std::cout << "===================================================================\n"
              << "  C++ Контролер лазерної платформи: Драйвер, Адаптація та Безпека  \n"
              << "===================================================================\n\n";

    // 1. Створення низькорівневих апаратних інтерфейсів
    HardwarePwmMock pwm_hw;
    HardwareSafetyMock safety_hw;

    // 2. Ініціалізація компонентів платформи за принципом інверсії залежностей
    laser::LaserOutput laser_out(pwm_hw, 25000); // 25 кГц несуча ШІМ для усунення смуг ковзного затвора

    laser::StrobeTimingConfig timing_cfg;
    timing_cfg.pulse_width_us = 300; // 300 мкс спалах діода на кадр
    timing_cfg.mode = laser::StrobeMode::ExternalTrigger;
    laser::StrobeController strobe_ctrl(laser_out, timing_cfg);

    laser::AmbientAdaptor ambient_adaptor(100, 900); // Діапазон заповнення 10% .. 90%
    laser::ThermalGuard thermal_guard;
    laser::SafetySupervisor safety_sup(laser_out, thermal_guard, safety_hw);

    std::cout << "[ІНІЦІАЛІЗАЦІЯ] Усі підсистеми зконфігуровано. RAII-драйвер готовий.\n\n";

    // 3. Симуляція роботи системи в динамічних сценаріях
    using namespace std::chrono;
    auto start_time = steady_clock::now();

    const auto get_ms = [&]() -> uint32_t {
        return static_cast<uint32_t>(duration_cast<milliseconds>(steady_clock::now() - start_time).count());
    };

    // СЦЕНАРІЙ 1: Адаптація до освітлення та штатні строби
    std::cout << "--- Сценарій 1: Штатні кадри з адаптацією яскравості до світла ---\n";
    const uint32_t test_lux_levels[] = {120, 1500, 45000};

    for (int i = 0; i < 3; ++i) {
        uint32_t now = get_ms();
        thermal_guard.update(now);

        // Перевірка безпеки перед запуском випромінювання
        if (!safety_sup.evaluate_safety()) {
            std::cout << "[ВІДМОВА] Спрацював захист: " << fault_to_string(safety_sup.current_fault()) << "\n";
            break;
        }

        // 1. Розрахунок яскравості за зовнішнім освітленням
        const uint32_t ambient_lux = test_lux_levels[i];
        const uint16_t adapted_duty = ambient_adaptor.calculate_duty(ambient_lux);

        // 2. Коригування шпаруватості через модель теплового балансу
        const uint16_t safe_duty = thermal_guard.clamp_duty(adapted_duty);

        // 3. Імітація приходу імпульсу експозиції від камери
        strobe_ctrl.on_external_trigger(safe_duty);

        // 4. Фіксація витрати теплового бюджету
        thermal_guard.register_pulse(timing_cfg.pulse_width_us, safe_duty);

        std::cout << "  Кадр " << (i + 1) << " | Освітленість: " << std::setw(6) << ambient_lux << " лк"
                  << " -> ШІМ: " << std::setw(4) << (safe_duty / 10.0f) << "%"
                  << " | Затвор MOSFET: " << (pwm_hw.is_active() ? "АКТИВНИЙ" : "ВИМК")
                  << " | Тепловий баланс: " << thermal_guard.thermal_load_percent() << "%\n";

        // Завершення спалаху (імітація затримки мікросекундного таймера)
        strobe_ctrl.on_pulse_complete();
        std::this_thread::sleep_for(milliseconds(25));
    }

    // СЦЕНАРІЙ 2: Високочастотна серія спалахів та тротлінг за моделлю leaky bucket
    std::cout << "\n--- Сценарій 2: Інтенсивна серія стробів -> Тепловий захист (Leaky Bucket) ---\n";
    for (int burst = 1; burst <= 6; ++burst) {
        uint32_t now = get_ms();
        thermal_guard.update(now);

        // Бажана потужність 90% при яскравому світлі
        const uint16_t requested_duty = 900;
        const uint16_t clamped_duty = thermal_guard.clamp_duty(requested_duty);

        // Застосування стробу
        strobe_ctrl.on_external_trigger(clamped_duty);
        thermal_guard.register_pulse(15000, clamped_duty); // Довгий цикл активності для нагріву
        strobe_ctrl.on_pulse_complete();

        std::cout << "  Імпульс " << burst << " | Запит: " << (requested_duty / 10.0f) << "%"
                  << " -> Видано: " << (clamped_duty / 10.0f) << "%"
                  << " | Нагрів: " << std::setw(3) << thermal_guard.thermal_load_percent() << "%"
                  << (thermal_guard.is_throttling() ? " [АКТИВОВАНО ТРОТЛІНГ!]" : "") << "\n";
    }

    // СЦЕНАРІЙ 3: Аварійне спрацювання фізичного контуру Interlock (відкриття кожуха)
    std::cout << "\n--- Сценарій 3: Аварійне розмикання контуру Interlock ---\n";
    std::cout << "[ПОДІЯ] Оператор відкрив захисний кожух установки (розрив ланцюга)...\n";
    safety_hw.set_interlock(false); // Фізичний розрив

    const bool safety_ok = safety_sup.evaluate_safety();
    std::cout << "  Стан супервізора: " << (safety_ok ? "ОК" : "АВАРІЯ!")
              << " | Діагностика: " << fault_to_string(safety_sup.current_fault())
              << " | Затвор N-MOSFET: " << (pwm_hw.is_active() ? "УВІМКНЕНО" : "ЗНЕСТРУМЛЕНО (0 В)") << "\n";

    // Спроба повторного запуску під час активної аварії
    strobe_ctrl.on_external_trigger(500);
    std::cout << "  Спроба запуску спалаху під час аварії -> Затвор: "
              << (pwm_hw.is_active() ? "УВІМКНЕНО" : "БЛОКОВАНО RAII-ЗАХИСТОМ") << "\n";

    // Відновлення ланцюга та скидання помилки
    std::cout << "\n[ВІДНОВЛЕННЯ] Закриття кожуха та скидання помилки...\n";
    safety_hw.set_interlock(true);
    if (safety_sup.try_clear_fault()) {
        std::cout << "  Помилку успішно знято: " << fault_to_string(safety_sup.current_fault()) << "\n";
    }

    std::cout << "\n[ДЕСТРУКЦІЯ] Завершення програми: деструктори об'єктів гарантовано очищують стан заліза.\n";
    return 0;
}
