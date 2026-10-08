#ifndef SERVO_PWM_HPP
#define SERVO_PWM_HPP

#include <cstdint>

namespace actuators {

/// @brief Конфігураційні параметри ШІМ-сигналу керування сервоприводом MG90S V2.
struct ServoPwmConfig {
    uint8_t pin{9};                     // Номер сигнального виходу КМОП/ШІМ
    uint32_t frequency_hz{50};          // Базова частота ШІМ для сервоприводів (50 Гц, період 20 мс)
    uint16_t min_pulse_us{500};         // Мінімальна тривалість імпульсу (відповідає 0°)
    uint16_t max_pulse_us{2500};        // Максимальна тривалість імпульсу (відповідає 180°)
    float min_angle_deg{0.0f};          // Мінімальний фізичний кут позиціонування
    float max_angle_deg{180.0f};        // Максимальний фізичний кут позиціонування
};

/// @brief Клас для низькорівневої генерації ШІМ-сигналу керування сервоприводом.
class ServoPwmGenerator {
public:
    /// @brief Конструктор із можливістю передачі власної конфігурації.
    explicit ServoPwmGenerator(const ServoPwmConfig& config = ServoPwmConfig{});

    /// @brief Ініціалізація ШІМ-периферії та налаштування таймера.
    /// @return true, якщо ініціалізація успішна.
    bool initialize();

    /// @brief Увімкнення подачі ШІМ-сигналу на вихідний піно.
    void enable();

    /// @brief Вимкнення подачі ШІМ-сигналу (зняття напруги керування).
    void disable();

    /// @brief Перевірка активності ШІМ-виходу.
    bool is_enabled() const;

    /// @brief Встановлення кута повороту сервопривода.
    /// @param angle_deg Кут у градусах.
    /// @return true, якщо кут в межах дозволеного діапазону.
    bool set_angle(float angle_deg);

    /// @brief Пряме встановлення тривалості ШІМ-імпульсу у мікросекундах.
    /// @param pulse_us Тривалість імпульсу у мкс.
    /// @return true, якщо тривалість успішно застосована.
    bool set_pulse_width_us(uint16_t pulse_us);

    /// @brief Отримання поточного встановленого кута.
    float get_current_angle() const;

    /// @brief Отримання поточної тривалості імпульсу в мікросекундах.
    uint16_t get_current_pulse_us() const;

    /// @brief Отримання поточної конфігурації генератора.
    const ServoPwmConfig& get_config() const;

    /// @brief Мапування кута у мікросекунди тривалості імпульсу.
    uint16_t angle_to_pulse_us(float angle_deg) const;

    /// @brief Зворотне мапування тривалості імпульсу в кут у градусах.
    float pulse_us_to_angle(uint16_t pulse_us) const;

private:
    ServoPwmConfig config_;
    bool enabled_{false};
    float current_angle_deg_{90.0f};
    uint16_t current_pulse_us_{1500};

    float clamp_angle(float angle_deg) const;
    uint16_t clamp_pulse_us(uint16_t pulse_us) const;
    void apply_hardware_pwm(uint16_t pulse_us);
};

} // namespace actuators

#endif // SERVO_PWM_HPP
