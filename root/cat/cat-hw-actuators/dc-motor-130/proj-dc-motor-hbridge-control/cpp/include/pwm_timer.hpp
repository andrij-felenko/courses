#ifndef PWM_TIMER_HPP
#define PWM_TIMER_HPP

#include <cstdint>

namespace embedded {

/**
 * @brief Клас для низькорівневого керування виводами GPIO та апаратним таймером ШІМ.
 * 
 * Відповідає за маніпуляцію виводами напрямку (IN1, IN2) та генерування високочастотного
 * ШІМ-сигналу на виводі дозволу (EN/PWM) для керування силовим H-мостом.
 */
class PwmTimer {
public:
    /**
     * @brief Конструктор периферійного контролера ШІМ.
     * @param pinIn1 Номер GPIO виводу IN1
     * @param pinIn2 Номер GPIO виводу IN2
     * @param pinEnable Номер GPIO виводу EN/PWM
     * @param frequencyHz Бажана частота ШІМ у Гц (за замовчуванням 20 000 Гц)
     */
    PwmTimer(uint8_t pinIn1, uint8_t pinIn2, uint8_t pinEnable, uint32_t frequencyHz = 20000);

    ~PwmTimer() = default;

    /**
     * @brief Ініціалізація виводів GPIO та апаратного таймера мікроконтролера.
     * @return true у разі успішної конфігурації периферії
     */
    bool init();

    /**
     * @brief Встановлення дискретних рівнів на виводах напрямку IN1 та IN2.
     * @param in1 Логічний рівень для IN1 (true = HIGH, false = LOW)
     * @param in2 Логічний рівень для IN2 (true = HIGH, false = LOW)
     */
    void setDirectionPins(bool in1, bool in2);

    /**
     * @brief Задання коефіцієнта заповнення ШІМ (Duty Cycle) у відсотках (0–100%).
     * @param dutyPercent Значення коефіцієнта заповнення у відсотках
     */
    void setPwmDuty(uint8_t dutyPercent);

    /**
     * @brief Аварійна або примусова зупинка генерації ШІМ (0% заповнення).
     */
    void stopPwm();

    /**
     * @brief Отримання налаштованої частоти ШІМ у Гц.
     */
    [[nodiscard]] uint32_t getFrequency() const noexcept { return frequencyHz_; }

    /**
     * @brief Отримання поточного встановленого коефіцієнта заповнення ШІМ.
     */
    [[nodiscard]] uint8_t getCurrentDuty() const noexcept { return currentDutyPercent_; }

    /**
     * @brief Перевірка статусу ініціалізації периферії.
     */
    [[nodiscard]] bool isInitialized() const noexcept { return initialized_; }

    /**
     * @brief Системна затримка у мілісекундах для формування Dead Time.
     * @param ms Час затримки в мілісекундах
     */
    static void delayMs(uint32_t ms);

private:
    uint8_t pinIn1_;
    uint8_t pinIn2_;
    uint8_t pinEnable_;
    uint32_t frequencyHz_;
    uint8_t currentDutyPercent_{0};
    bool initialized_{false};

    [[nodiscard]] uint16_t calculateCompareValue(uint8_t dutyPercent) const noexcept;
};

} // namespace embedded

#endif // PWM_TIMER_HPP
