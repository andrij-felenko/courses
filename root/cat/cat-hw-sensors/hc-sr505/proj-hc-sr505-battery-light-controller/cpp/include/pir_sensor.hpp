#ifndef PIR_SENSOR_HPP
#define PIR_SENSOR_HPP

#include <cstdint>
#include <atomic>

/**
 * @brief Перерахування станів відстеження руху давачем HC-SR505.
 */
enum class MotionState : uint8_t {
    NoMotion = 0,   ///< Руху не виявлено (низький рівень на виході OUT)
    MotionDetected  ///< Виявлено рух (високий рівень на виході OUT)
};

/**
 * @brief Драйвер-обгортка мініатюрного PIR-давача HC-SR505.
 * 
 * Клас забезпечує потокобезпечне та ISR-safe читання стану цифрового виходу
 * HC-SR505, фіксацію подій через апаратне переривання EXTI та фільтрацію
 * можливих дребезгів чи коротких хибних спрацювань.
 */
class PirSensor {
public:
    /**
     * @brief Конструктор драйвера давача.
     * @param gpio_pin Номер цифрового виводу мікроконтролера, підключеного до OUT HC-SR505.
     * @param debounce_ms Час програмної фільтрації (дребезгу) у мілісекундах.
     */
    explicit PirSensor(uint8_t gpio_pin, uint32_t debounce_ms = 50);

    /**
     * @brief Ініціалізація GPIO та налаштування зовнішнього переривання (EXTI).
     */
    void init();

    /**
     * @brief Обробник апаратного переривання (ISR-safe).
     * 
     * Метод викликається у контексті переривання за зміною стану лінії (RISING / FALLING).
     * Атомарно оновлює прапорці та фіксує поточний рівень сигналу.
     * 
     * @param current_pin_level Поточний логічний рівень на виводі (true = HIGH, false = LOW).
     * @param current_time_ms Поточний системний час у мілісекундах.
     */
    void handleInterrupt(bool current_pin_level, uint32_t current_time_ms);

    /**
     * @brief Перевіряє, чи виявлено рух у даний момент.
     * @return true, якщо давач утримує високий рівень сигналу.
     */
    bool isMotionDetected() const;

    /**
     * @brief Перевіряє наявність незафіксованої події початку руху та скидає її прапорець.
     * @return true, якщо з моменту останнього виклику було зафіксовано новий рух.
     */
    bool consumeMotionEvent();

    /**
     * @brief Отримати номер GPIO виводу давача.
     */
    uint8_t getPin() const { return pin_; }

private:
    uint8_t pin_;
    uint32_t debounce_ms_;

    // Атомні прапорці для безпечної передачі даних з ISR у головний цикл
    std::atomic<bool> is_active_{false};
    std::atomic<bool> motion_event_pending_{false};
    std::atomic<uint32_t> last_interrupt_time_{0};
};

#endif // PIR_SENSOR_HPP
