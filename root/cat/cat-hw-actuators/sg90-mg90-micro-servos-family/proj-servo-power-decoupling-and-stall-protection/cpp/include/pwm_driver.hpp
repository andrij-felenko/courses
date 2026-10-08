#ifndef PWM_DRIVER_HPP
#define PWM_DRIVER_HPP

#include <cstdint>

namespace towerpro {

/**
 * @brief Клас для низькорівневого формування керуючого 50 Гц ШІМ-сигналу сервоприводу.
 * 
 * Період ШІМ становить 20 мс (50 Гц). Підтримується регулювання тривалості імпульсу 
 * у мікросекундах (500–2500 мкс) та миттєве апаратне зняття ШІМ-сигналу (detach).
 */
class PwmDriver {
public:
    PwmDriver() = default;
    ~PwmDriver();

    PwmDriver(const PwmDriver&) = delete;
    PwmDriver& operator=(const PwmDriver&) = delete;

    /**
     * @brief Ініціалізація виводу ШІМ.
     * @param pin Номер керуючого виводу мікроконтролера.
     * @return true у разі успішного призначення виводу.
     */
    bool begin(uint8_t pin);

    /**
     * @brief Задати тривалість керуючого імпульсу в мікросекундах.
     * @param pulseUs Тривалість імпульсу у діапазоні 500..2500 мкс.
     */
    void writeMicroseconds(uint16_t pulseUs);

    /**
     * @brief Апаратне зняття ШІМ-сигналу з виводу (знеструмлення обмоток).
     */
    void detach();

    /**
     * @brief Відновлення генерації ШІМ-сигналу на виводі.
     */
    void attach();

    /**
     * @brief Перевірка активності ШІМ-сигналу.
     */
    bool isAttached() const;

    /**
     * @brief Отримати поточне значення тривалості імпульсу (мкс).
     */
    uint16_t getPulseMicroseconds() const;

    /**
     * @brief Отримати номер виводу ШІМ.
     */
    uint8_t getPin() const;

private:
    uint8_t pin_{0};
    uint16_t currentPulseUs_{1500};
    bool attached_{false};

    void hardwareSetPulse(uint16_t pulseUs);
    void hardwareDetach();
};

} // namespace towerpro

#endif // PWM_DRIVER_HPP
