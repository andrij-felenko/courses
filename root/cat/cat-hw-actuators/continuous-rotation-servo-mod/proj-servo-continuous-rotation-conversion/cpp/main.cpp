#include "continuous_rotation_servo.hpp"

#include <iostream>
#include <iomanip>
#include <cstdint>

/**
 * @brief Емуляція апаратного ШІМ-каналу таймера мікроконтролера.
 * Реалізує інтерфейс IPwmOutput, дозволяючи тестувати драйвер без прив'язки до заліза.
 */
class SimulatedPwmTimer final : public motion::IPwmOutput {
public:
    explicit SimulatedPwmTimer(uint8_t channel_index) noexcept
        : channel_index_(channel_index) {}

    void write_pulse_us(uint16_t pulse_us) noexcept override {
        pulse_us_ = pulse_us;
    }

    void disable() noexcept override {
        is_active_ = false;
    }

    void enable() noexcept override {
        is_active_ = true;
    }

    [[nodiscard]] bool is_active() const noexcept override {
        return is_active_;
    }

    [[nodiscard]] uint16_t current_pulse() const noexcept {
        return pulse_us_;
    }

    [[nodiscard]] uint8_t channel() const noexcept {
        return channel_index_;
    }

private:
    uint8_t channel_index_{0};
    uint16_t pulse_us_{1500};
    bool is_active_{false};
};

/**
 * @brief Допоміжна функція для текстового представлення стану драйвера.
 */
static const char* drive_state_str(motion::DriveState state) noexcept {
    switch (state) {
        case motion::DriveState::Detached:       return "Знеструмлено (Detached)";
        case motion::DriveState::Stopped:        return "Спокій (Stopped)";
        case motion::DriveState::Running:        return "Рух (Running)";
        case motion::DriveState::ReversingDwell: return "Витримка реверсу (Dwell)";
        default:                                 return "Невідомо";
    }
}

int main() {
    std::cout << "===============================================================================\n";
    std::cout << "  Демонстрація C++ драйвера сервопривода постійного обертання (Continuous Servo)\n";
    std::cout << "===============================================================================\n\n";

    // 1. Створення апаратного каналу ШІМ (наприклад, Timer 1 Channel 0)
    SimulatedPwmTimer pwm_hardware(1);

    // 2. Налаштування індивідуального калібрування сервопривода:
    // Через технологічний розкид внутрішнього дільника напруги точка зупинки вала
    // зсунута з номінальних 1500 мкс до 1525 мкс.
    // Задаємо напівширину мертвої зони (deadband) 25 мкс для надійного блокування дрейфу.
    motion::ServoCalibration calibration{};
    calibration.neutral_us = 1525;    // Виміряна нейтральна точка спокою вала
    calibration.deadband_us = 25;     // Мертва смуга [1500..1550] мкс для захисту від дрейфу
    calibration.min_pulse_us = 1000;  // Максимальний хід назад (1000 мкс)
    calibration.max_pulse_us = 2000;  // Максимальний хід вперед (2000 мкс)
    calibration.inverted = false;     // Звичайний напрямок обертання

    if (!calibration.is_valid()) {
        std::cerr << "Помилка: невалідні параметри калібрування сервопривода!\n";
        return 1;
    }

    std::cout << "[Калібрування]\n";
    std::cout << "  Нейтраль (спокій): " << calibration.neutral_us << " мкс\n";
    std::cout << "  Мертва смуга:     ±" << calibration.deadband_us << " мкс ["
              << (calibration.neutral_us - calibration.deadband_us) << " .. "
              << (calibration.neutral_us + calibration.deadband_us) << "] мкс\n";
    std::cout << "  Діапазон імпульсу: [" << calibration.min_pulse_us << " .. "
              << calibration.max_pulse_us << "] мкс\n\n";

    // 3. Ініціалізація екземпляра сервопривода:
    // Темп наростання швидкості dω/dt = 150 %/с (плавний розгін без ударів)
    // Пауза витримки реверсу = 40 мс (2 періоди ШІМ по 20 мс для заспокоєння редуктора)
    motion::ContinuousRotationServo servo(pwm_hardware, calibration, 150.0f, 40);

    // Підключення генерації ШІМ
    servo.attach();
    std::cout << "[Ініціалізація] Сервопривод активовано (attach). Початковий стан: "
              << drive_state_str(servo.state()) << ", імпульс: "
              << pwm_hardware.current_pulse() << " мкс.\n\n";

    // 4. Демонстрація неблокувального періодичного суперциклу керування (період квантування 20 мс / 50 Гц)
    constexpr uint32_t kLoopStepMs = 20;
    uint32_t current_time_ms = 0;

    auto print_telemetry_header = []() {
        std::cout << std::left
                  << std::setw(8)  << "Час (мс)"
                  << std::setw(12) << "Ціль (%)"
                  << std::setw(14) << "Поточна (%)"
                  << std::setw(14) << "Імпульс (мкс)"
                  << std::setw(10) << "ШІМ"
                  << "Стан привода\n";
        std::cout << std::string(75, '-') << "\n";
    };

    auto print_telemetry = [&](uint32_t t_ms) {
        std::cout << std::left
                  << std::setw(8)  << t_ms
                  << std::setw(12) << std::fixed << std::setprecision(1) << servo.target_speed()
                  << std::setw(14) << std::fixed << std::setprecision(1) << servo.current_speed()
                  << std::setw(14) << servo.current_pulse_us()
                  << std::setw(10) << (pwm_hardware.is_active() ? "ВКЛ" : "ВИМК")
                  << drive_state_str(servo.state()) << "\n";
    };

    print_telemetry_header();

    // СЦЕНАРІЙ РОБОТИ:
    // Етап 1 (0..600 мс): Плавний розгін вперед до +60%
    servo.set_speed(60.0f);
    for (; current_time_ms <= 600; current_time_ms += kLoopStepMs) {
        servo.update(current_time_ms);
        // Виводимо телеметрію кожні 100 мс для наочності
        if (current_time_ms % 100 == 0) {
            print_telemetry(current_time_ms);
        }
    }

    std::cout << "\n>>> Команда реверсу: зміна цільової швидкості з +60% на -60% <<<\n";
    std::cout << ">>> Спостерігаємо безпечне гальмування до 0, витримку Dwell та зміну знака <<<\n\n";

    // Етап 2 (620..1800 мс): Безпечний реверс на -60%
    servo.set_speed(-60.0f);
    for (; current_time_ms <= 1800; current_time_ms += kLoopStepMs) {
        servo.update(current_time_ms);
        // Виводимо частіше під час проходження нуля для спостереження Dwell
        if (current_time_ms % 60 == 0 || servo.state() == motion::DriveState::ReversingDwell) {
            print_telemetry(current_time_ms);
        }
    }

    std::cout << "\n>>> Команда повної зупинки вала (ціль 0%) <<<\n\n";

    // Етап 3 (1820..2400 мс): Плавна зупинка у нейтраль
    servo.set_speed(0.0f);
    for (; current_time_ms <= 2400; current_time_ms += kLoopStepMs) {
        servo.update(current_time_ms);
        if (current_time_ms % 100 == 0) {
            print_telemetry(current_time_ms);
        }
    }

    std::cout << "\n>>> Переведення сервопривода у режим знеструмлення (detach) під час простою <<<\n\n";

    // Етап 4 (2420..2600 мс): Знеструмлення привода
    servo.detach();
    for (; current_time_ms <= 2600; current_time_ms += kLoopStepMs) {
        servo.update(current_time_ms);
        if (current_time_ms % 100 == 0) {
            print_telemetry(current_time_ms);
        }
    }

    std::cout << "\n===============================================================================\n";
    std::cout << "  Демонстрацію успішно завершено: редуктор захищено від реверсивного удару,\n";
    std::cout << "  струмові стрибки усунуто рампінгом dω/dt, обмотки знеструмлено під час паузи.\n";
    std::cout << "===============================================================================\n";

    return 0;
}
