#ifndef MOSFET_PWM_HAL_HPP
#define MOSFET_PWM_HAL_HPP

#include <cstdint>

/**
 * @brief Низькорівневий клас-абстракція для керування силовим MOSFET-ключем помпи RS-360SH.
 * 
 * Клас інкапсулює роботу з апаратним ШІМ-таймером мікроконтролера, забезпечує
 * регулювання коефіцієнта заповнення (Duty Cycle) та миттєве аварійне знеструмлення.
 */
class MosfetPwmHal {
public:
    /**
     * @brief Конструктор HAL-модуля.
     * @param pwm_pin Номер фізичного виводу мікроконтролера (Gate MOSFET).
     * @param frequency_hz Базова частота ШІМ у Герцах (за замовчуванням 5000 Гц).
     */
    explicit MosfetPwmHal(std::uint8_t pwm_pin, std::uint32_t frequency_hz = 5000);

    /**
     * @brief Ініціалізація апаратного ШІМ-таймера та конфігурація GPIO.
     * @return true у разі успішної ініціалізації.
     */
    bool init();

    /**
     * @brief Встановлення коефіцієнта заповнення ШІМ.
     * @param duty_cycle Значення від 0.0 (0%) до 1.0 (100%).
     */
    void setDutyCycle(float duty_cycle);

    /**
     * @brief Отримання поточного встановленого значення ШІМ.
     * @return Коефіцієнт заповнення від 0.0 до 1.0.
     */
    float getDutyCycle() const;

    /**
     * @brief Негайне аварійне вимкнення ШІМ та скидання сигналу на затворі MOSFET у нуль.
     */
    void emergencyShutdown();

    /**
     * @brief Перевірка стану активності ШІМ-виходу.
     * @return true, якщо ШІМ ініціалізовано та вихід активовано.
     */
    bool isEnabled() const;

    /**
     * @brief Отримання налаштованої частоти ШІМ.
     * @return Частота в Герцах.
     */
    std::uint32_t getFrequency() const;

private:
    std::uint8_t pwm_pin_;
    std::uint32_t frequency_hz_;
    float current_duty_{0.0f};
    bool enabled_{false};
};

#endif // MOSFET_PWM_HAL_HPP
