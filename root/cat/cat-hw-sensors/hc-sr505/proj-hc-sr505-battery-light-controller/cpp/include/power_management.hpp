#ifndef POWER_MANAGEMENT_HPP
#define POWER_MANAGEMENT_HPP

#include <cstdint>

/**
 * @brief Режими зниженого енергоспоживання мікроконтролера.
 */
enum class LowPowerMode : uint8_t {
    Sleep,      ///< Легкий сон: ядро зупинено, периферія працює
    DeepSleep,  ///< Глибокий сон: тактування ядра та більшості периферії зупинено (Stop mode)
    Standby     ///< Режим очікування: мінімальне споживання, скидання системного стану
};

/**
 * @brief RAII-клас керування живленням та режимами сну мікроконтролера.
 * 
 * Відповідає за налаштування джерел пробудження (EXTI лінія HC-SR505),
 * безпечне переведення процесора в режим зниженого енергоспоживання та
 * відновлення системної тактової частоти після пробудження.
 */
class PowerManager {
public:
    /**
     * @brief Конструктор модуля живлення.
     * @param initial_mode Початковий режим зниженого енергоспоживання.
     */
    explicit PowerManager(LowPowerMode initial_mode = LowPowerMode::DeepSleep);

    /**
     * @brief Деструктор: забезпечує відновлення повнофункціонального стану живлення.
     */
    ~PowerManager();

    // Заборона копіювання для забезпечення RAII-семантики
    PowerManager(const PowerManager&) = delete;
    PowerManager& operator=(const PowerManager&) = delete;

    /**
     * @brief Конфігурація лінії зовнішнього переривання (EXTI) як джерела пробудження.
     * @param gpio_pin Номер виводу, до якого підключено HC-SR505.
     */
    void configureWakeupSource(uint8_t gpio_pin);

    /**
     * @brief Переведення мікроконтролера в сон до надходження переривання від давача.
     * 
     * Метод блокує виконання до моменту апаратного пробудження. Після виходу зі сну
     * автоматично викликає restoreSystemClock().
     */
    void enterSleep();

    /**
     * @brief Відновлення системних генераторів (PLL/HSI) та тактування периферії.
     */
    void restoreSystemClock();

    /**
     * @brief Встановити активний режим енергозбереження.
     */
    void setLowPowerMode(LowPowerMode mode) { low_power_mode_ = mode; }

    /**
     * @brief Перевірити, чи система перебуває у стані пробудження після сну.
     */
    bool wasWokenUp() const { return woken_up_; }

    /**
     * @brief Скинути прапорець фактів пробудження.
     */
    void clearWakeupFlag() { woken_up_ = false; }

private:
    LowPowerMode low_power_mode_;
    uint8_t wakeup_pin_{0};
    bool wakeup_configured_{false};
    bool woken_up_{false};
};

#endif // POWER_MANAGEMENT_HPP
