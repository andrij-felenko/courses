#ifndef PWM_TIMER_HPP
#define PWM_TIMER_HPP

#include <cstdint>
#include <algorithm>
#include <iostream>

/**
 * @brief Апаратна обгортка ШІМ-таймера мікроконтролера.
 * Забезпечує формування періодичного керуючого сигналу 50 Гц (період 20 мс)
 * з можливістю регулювання тривалості керуючого імпульсу у мікросекундах.
 */
class PwmTimer {
public:
    /**
     * @brief Конструктор апаратного ШІМ-таймера.
     * @param gpio_pin Номер виводу GPIO для генерирування ШІМ.
     * @param frequency_hz Частота ШІМ-сигналу в Гц (за замовчуванням 50 Гц).
     */
    explicit PwmTimer(uint8_t gpio_pin, uint32_t frequency_hz = 50)
        : gpio_pin_(gpio_pin),
          frequency_hz_(frequency_hz),
          period_us_(1000000U / (frequency_hz > 0 ? frequency_hz : 50)),
          current_pulse_us_(0),
          enabled_(false) {}

    /**
     * @brief Ініціалізація апаратного таймера та виводу GPIO.
     * @return true у разі успішної конфігурації апаратури.
     */
    bool init() {
        enabled_ = true;
        current_pulse_us_ = 1500; // Початковий нейтральний стан (1.5 мс)
        std::cout << "[PwmTimer] Ініціалізовано GPIO " << static_cast<int>(gpio_pin_)
                  << " | Частота: " << frequency_hz_ << " Гц (Період: "
                  << period_us_ << " мкс)\n";
        return true;
    }

    /**
     * @brief Встановлення тривалості керуючого імпульсу високого рівня.
     * @param pulse_us Тривалість імпульсу у мікросекундах.
     * @return true якщо значення в межах припустимого періоду.
     */
    bool setPulseWidthUs(uint16_t pulse_us) {
        if (!enabled_) {
            std::cerr << "[PwmTimer] Помилка: таймер на GPIO "
                      << static_cast<int>(gpio_pin_) << " не ініціалізовано!\n";
            return false;
        }

        if (pulse_us > period_us_) {
            std::cerr << "[PwmTimer] Помилка: тривалість імпульсу " << pulse_us
                      << " мкс перевищує період " << period_us_ << " мкс!\n";
            return false;
        }

        current_pulse_us_ = pulse_us;
        return true;
    }

    /**
     * @brief Вимкнення генерації ШІМ-сигналу.
     */
    void disable() {
        enabled_ = false;
        current_pulse_us_ = 0;
        std::cout << "[PwmTimer] Генерацію ШІМ на GPIO "
                  << static_cast<int>(gpio_pin_) << " зупинено.\n";
    }

    /// Отримання номера виводу GPIO
    uint8_t getPin() const noexcept { return gpio_pin_; }

    /// Отримання частоти таймера в Гц
    uint32_t getFrequencyHz() const noexcept { return frequency_hz_; }

    /// Отримання періоду таймера в мікросекундах
    uint32_t getPeriodUs() const noexcept { return period_us_; }

    /// Отримання поточної тривалості імпульсу в мікросекундах
    uint16_t getActivePulseUs() const noexcept { return current_pulse_us_; }

    /// Перевірка стану активності ШІМ
    bool isEnabled() const noexcept { return enabled_; }

private:
    uint8_t gpio_pin_;
    uint32_t frequency_hz_;
    uint32_t period_us_;
    uint16_t current_pulse_us_;
    bool enabled_;
};

#endif // PWM_TIMER_HPP
