#include "dc_motor_130.hpp"

#include <iostream>
#include <iomanip>
#include <string>

/**
 * @brief Платформова реалізація інтерфейсу IHBridgeOutput.
 * 
 * Емулює фізичну поведінку інтегрального H-моста (наприклад, DRV8833, TB6612FNG або L9110S),
 * підключеного до каналів апаратного таймера ШІМ мікроконтролера.
 * На реальному контролері (STM32, ESP32, AVR, RP2040) виклики транслюються
 * у запис регістрів CCR таймера або відповідні функції HAL.
 */
class PlatformHBridge final : public motion::IHBridgeOutput {
public:
    enum class OutputMode : uint8_t {
        Coast_HiZ = 0,    ///< Ключі моста розімкнені (стан високого імпедансу)
        DynamicBrake,     ///< Обидва виводи замкнені накоротко (динамічне гальмо)
        PwmForward,       ///< IN1 = PWM, IN2 = 0 (прямий хід)
        PwmReverse        ///< IN1 = 0, IN2 = PWM (реверс)
    };

    bool init(uint8_t pin_forward, uint8_t pin_reverse, uint32_t pwm_freq_hz) noexcept override {
        pin_fwd_ = pin_forward;
        pin_rev_ = pin_reverse;
        pwm_freq_hz_ = pwm_freq_hz;
        duty_fwd_ = 0.0f;
        duty_rev_ = 0.0f;
        mode_ = OutputMode::Coast_HiZ;
        is_ready_ = true;
        return true;
    }

    void set_forward(float duty_pct) noexcept override {
        mode_ = OutputMode::PwmForward;
        duty_fwd_ = duty_pct;
        duty_rev_ = 0.0f;
        // На реальному мікроконтролері (наприклад, STM32 HAL):
        // __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, (uint32_t)(duty_pct * max_ticks / 100.0f));
        // __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_2, 0);
    }

    void set_reverse(float duty_pct) noexcept override {
        mode_ = OutputMode::PwmReverse;
        duty_fwd_ = 0.0f;
        duty_rev_ = duty_pct;
        // На реальному мікроконтролері (наприклад, STM32 HAL):
        // __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, 0);
        // __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_2, (uint32_t)(duty_pct * max_ticks / 100.0f));
    }

    void set_dynamic_brake() noexcept override {
        mode_ = OutputMode::DynamicBrake;
        duty_fwd_ = 100.0f;
        duty_rev_ = 100.0f;
        // На реальному драйвері (DRV8833/TB6612):
        // Обидва керуючі виводи переводяться у логічну одиницю (HIGH)
        // або обидва нижні польові ключі відкриваються, закорочуючи обмотку ротора.
    }

    void set_coast() noexcept override {
        mode_ = OutputMode::Coast_HiZ;
        duty_fwd_ = 0.0f;
        duty_rev_ = 0.0f;
        // На реальному мікроконтролері:
        // ШІМ-канали переводяться у 0%, вихідні каскади знеструмлюються (Hi-Z).
    }

    [[nodiscard]] OutputMode output_mode() const noexcept { return mode_; }
    [[nodiscard]] float forward_duty() const noexcept { return duty_fwd_; }
    [[nodiscard]] float reverse_duty() const noexcept { return duty_rev_; }
    [[nodiscard]] uint8_t pin_forward() const noexcept { return pin_fwd_; }
    [[nodiscard]] uint8_t pin_reverse() const noexcept { return pin_rev_; }

    [[nodiscard]] const char* output_mode_str() const noexcept {
        switch (mode_) {
            case OutputMode::Coast_HiZ:    return "Coast (Hi-Z)";
            case OutputMode::DynamicBrake: return "Dynamic Brake";
            case OutputMode::PwmForward:   return "PWM Forward";
            case OutputMode::PwmReverse:   return "PWM Reverse";
            default:                       return "Невідомо";
        }
    }

private:
    uint8_t pin_fwd_{0};
    uint8_t pin_rev_{0};
    uint32_t pwm_freq_hz_{20000};
    float duty_fwd_{0.0f};
    float duty_rev_{0.0f};
    OutputMode mode_{OutputMode::Coast_HiZ};
    bool is_ready_{false};
};

/**
 * @brief Допоміжне текстове представлення стану привода.
 */
static const char* drive_state_to_str(motion::DriveState state) noexcept {
    switch (state) {
        case motion::DriveState::Coast:    return "Coast (Вибіг)";
        case motion::DriveState::Braking:  return "Braking (Гальмо)";
        case motion::DriveState::Forward:  return "Forward (Вперед)";
        case motion::DriveState::Reverse:  return "Reverse (Назад)";
        case motion::DriveState::DeadTime: return "DeadTime (Пауза)";
        default:                           return "Невідомо";
    }
}

int main() {
    std::cout << "===============================================================================\n";
    std::cout << "  Драйвер колекторного двигуна типорозміру 130 на C++ (Soft-Start / Dead-Time)  \n";
    std::cout << "===============================================================================\n\n";

    // 1. Створення апаратного інтерфейсу H-моста
    PlatformHBridge hardware_bridge;

    // 2. Налаштування параметрів привода
    // - ШІМ 20 кГц (вище межі чутності людського вуха, запобігає пищанню мотора)
    // - Dead-time 50 мкс (достатньо для повного розряджання затворів MOSFET у H-мості)
    // - Темп рампи soft-start 200 %/с (плавний розгін за 500 мс без стрибків струму заклинювання)
    // - Мінімальна шпаруватість 12% (подолання сухого тертя щіток і редуктора)
    motion::MotorConfig config{};
    config.pin_forward = 9;              // Наприклад, вивід TIM1_CH1
    config.pin_reverse = 10;             // Наприклад, вивід TIM1_CH2
    config.pwm_frequency_hz = 20000;     // 20 кГц
    config.dead_time_us = 50;            // 50 мкс захисного мертвого часу
    config.max_slew_rate_pct_per_s = 200.0f; // 200 %/с
    config.min_start_duty_pct = 12.0f;   // 12%
    config.default_stop_mode = motion::StopMode::Coast;

    if (!config.is_valid()) {
        std::cerr << "Помилка: невалідні параметри конфігурації двигуна!\n";
        return 1;
    }

    // 3. Ініціалізація екземпляра класу-драйвера DcMotor130
    motion::DcMotor130 motor(hardware_bridge, config);
    if (!motor.init()) {
        std::cerr << "Помилка: збій ініціалізації апаратного моста!\n";
        return 1;
    }

    std::cout << "[Конфігурація]\n";
    std::cout << "  Виводи керування: IN1 = D" << static_cast<int>(config.pin_forward)
              << ", IN2 = D" << static_cast<int>(config.pin_reverse) << "\n";
    std::cout << "  Частота ШІМ: " << config.pwm_frequency_hz << " Гц (20 кГц)\n";
    std::cout << "  Захисний мертвий час: " << config.dead_time_us << " мкс\n";
    std::cout << "  Темп soft-start наростання: " << config.max_slew_rate_pct_per_s << " %/с\n";
    std::cout << "  Поріг подолання тертя: " << config.min_start_duty_pct << " %\n\n";

    // Форматування шапки таблиці телеметрії
    auto print_header = []() {
        std::cout << std::left
                  << std::setw(9)  << "Час(мс)"
                  << std::setw(15) << "Режим моста"
                  << std::setw(11) << "Ціль(%)"
                  << std::setw(15) << "Швидкість(%)"
                  << std::setw(13) << "ШІМ Fwd(%)"
                  << std::setw(13) << "ШІМ Rev(%)"
                  << "Стан драйвера\n";
        std::cout << std::string(85, '-') << "\n";
    };

    auto print_telemetry = [&](uint32_t time_ms) {
        std::cout << std::left
                  << std::setw(9)  << time_ms
                  << std::setw(15) << hardware_bridge.output_mode_str()
                  << std::setw(11) << std::fixed << std::setprecision(1) << motor.target_speed()
                  << std::setw(15) << std::fixed << std::setprecision(1) << motor.current_speed()
                  << std::setw(13) << std::fixed << std::setprecision(1) << hardware_bridge.forward_duty()
                  << std::setw(13) << std::fixed << std::setprecision(1) << hardware_bridge.reverse_duty()
                  << drive_state_to_str(motor.state()) << "\n";
    };

    // 4. Демонстраційний суперцикл керування (квант часу 20 мс = 50 Гц)
    constexpr uint32_t kLoopStepMs = 20;
    constexpr uint32_t kLoopStepUs = kLoopStepMs * 1000U;
    uint32_t current_time_us = 0;

    print_header();

    // =========================================================================
    // ЕТАП 1: Плавний пуск (Soft-Start) у напрямку Forward до +80%
    // Обмеження похідної dD/dt запобігає стрибку струму до 2.5 А та просіданню VCC
    // =========================================================================
    motor.set_speed(80.0f);
    for (; current_time_us <= 600000U; current_time_us += kLoopStepUs) {
        motor.update(current_time_us);
        const uint32_t time_ms = current_time_us / 1000U;
        if (time_ms % 100 == 0 || motor.state() == motion::DriveState::DeadTime) {
            print_telemetry(time_ms);
        }
    }

    // =========================================================================
    // ЕТАП 2: Контрольований реверс від +80% до -80%
    // 1) Сповільнення вперед до нуля (захист шестерень редуктора від удару)
    // 2) Захисна витримка dead-time (усунення наскрізного струму між стійками моста)
    // 3) Плавний розгін у зворотному напрямку soft-start
    // =========================================================================
    std::cout << "\n>>> Команда реверсу: перехід з +80% на -80% <<<\n";
    std::cout << ">>> Спостерігаємо сповільнення до 0, dead-time паузу і плавний розгін назад <<<\n\n";

    motor.set_speed(-80.0f);
    for (; current_time_us <= 1800000U; current_time_us += kLoopStepUs) {
        motor.update(current_time_us);
        const uint32_t time_ms = current_time_us / 1000U;
        // Виводимо частіше в зоні зміни знака швидкості
        if (time_ms % 100 == 0 || motor.is_in_dead_time() || std::abs(motor.current_speed()) < 15.0f) {
            print_telemetry(time_ms);
        }
    }

    // =========================================================================
    // ЕТАП 3: Плавне гальмування з активацією Dynamic Brake (проти-ЕРС)
    // Замикання клем двигуна створює генераторне навантаження для миттєвої фіксації
    // =========================================================================
    std::cout << "\n>>> Команда керованої зупинки з динамічним гальмуванням проти-ЕРС <<<\n\n";

    motor.stop(motion::StopMode::DynamicBrake);
    for (; current_time_us <= 2500000U; current_time_us += kLoopStepUs) {
        motor.update(current_time_us);
        const uint32_t time_ms = current_time_us / 1000U;
        if (time_ms % 100 == 0 || motor.is_in_dead_time() || motor.state() == motion::DriveState::Braking) {
            print_telemetry(time_ms);
        }
    }

    // =========================================================================
    // ЕТАП 4: Порівняння з режимом Coast (вільний вибіг)
    // =========================================================================
    std::cout << "\n>>> Порівняння: розгін до +50% та зупинка у режимі вільного вибігу (Coast) <<<\n\n";

    motor.set_speed(50.0f);
    for (uint32_t t_end = current_time_us + 400000U; current_time_us <= t_end; current_time_us += kLoopStepUs) {
        motor.update(current_time_us);
        const uint32_t time_ms = current_time_us / 1000U;
        if (time_ms % 100 == 0) {
            print_telemetry(time_ms);
        }
    }

    motor.stop(motion::StopMode::Coast);
    for (uint32_t t_end = current_time_us + 300000U; current_time_us <= t_end; current_time_us += kLoopStepUs) {
        motor.update(current_time_us);
        const uint32_t time_ms = current_time_us / 1000U;
        if (time_ms % 100 == 0 || motor.state() == motion::DriveState::Coast) {
            print_telemetry(time_ms);
        }
    }

    // =========================================================================
    // ЕТАП 5: Екстрена зупинка (Emergency Stop)
    // Миттєвий перехід до динамічного гальма в обхід темпу рампи
    // =========================================================================
    std::cout << "\n>>> Екстрена зупинка (Emergency Brake) на повному ходу <<<\n\n";

    motor.set_speed(70.0f);
    for (uint32_t t_end = current_time_us + 300000U; current_time_us <= t_end; current_time_us += kLoopStepUs) {
        motor.update(current_time_us);
        const uint32_t time_ms = current_time_us / 1000U;
        if (time_ms % 100 == 0) {
            print_telemetry(time_ms);
        }
    }

    std::cout << ">>> ВИКЛИК emergency_stop(DynamicBrake) <<<\n";
    motor.emergency_stop(motion::StopMode::DynamicBrake, current_time_us);
    for (uint32_t t_end = current_time_us + 100000U; current_time_us <= t_end; current_time_us += kLoopStepUs) {
        motor.update(current_time_us);
        const uint32_t time_ms = current_time_us / 1000U;
        print_telemetry(time_ms);
    }

    std::cout << "\n===============================================================================\n";
    std::cout << "  Демонстрацію успішно завершено: RAII автоматично знеструмить міст при виході.\n";
    std::cout << "===============================================================================\n";

    return 0;
}
