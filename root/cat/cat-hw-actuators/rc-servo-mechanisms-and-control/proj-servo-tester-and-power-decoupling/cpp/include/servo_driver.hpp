#ifndef SERVO_DRIVER_HPP
#define SERVO_DRIVER_HPP

#include <cstdint>

namespace rc_servo {

/**
 * @brief Результат виконання операцій з керування драйвером сервоприводу.
 */
enum class DriverStatus : uint8_t {
    Ok = 0,                     /*!< Операція виконана успішно */
    ErrAngleOutOfBounds,        /*!< Заданий кут виходить за допустимі межі (0..180°) */
    ErrPulseWidthOutOfBounds,   /*!< Задана тривалість імпульсу виходить за безпечний діапазон */
    ErrDisabled                 /*!< Спроба встановлення параметрів при вимкненому виході ШІМ */
};

/**
 * @brief Низькорівневий C++ драйвер для створення ШІМ-сигналу керування RC-сервоприводом.
 *
 * Драйвер працює з апаратним таймером мікроконтролера, оперуючи кадрами тривалістю 20 мс (50 Гц)
 * та тривалістю позитивного імпульсу в межах 500..2500 мкс (типово від 0° до 180°).
 */
class ServoDriver {
public:
    static constexpr uint16_t DEFAULT_MIN_PULSE_US = 500;   /*!< Стандартний мінімальний імпульс (0.5 мс = 0°) */
    static constexpr uint16_t DEFAULT_MAX_PULSE_US = 2500;  /*!< Стандартний максимальний імпульс (2.5 мс = 180°) */
    static constexpr uint16_t FRAME_PERIOD_US = 20000;       /*!< Загальний період кадру ШІМ (20 мс / 50 Гц) */
    static constexpr float MIN_ANGLE_DEG = 0.0f;             /*!< Мінімальний фізичний кут повороту */
    static constexpr float MAX_ANGLE_DEG = 180.0f;           /*!< Максимальний фізичний кут повороту */
    static constexpr uint32_t TIMER_CLOCK_HZ = 2000000UL;   /*!< Частота тактування таймера (2 МГц -> 0.5 мкс/відлік) */

    ServoDriver();
    explicit ServoDriver(uint8_t channel, 
                        uint16_t minPulseUs = DEFAULT_MIN_PULSE_US, 
                        uint16_t maxPulseUs = DEFAULT_MAX_PULSE_US);

    /**
     * @brief Конфігурування апаратного каналу та робочих меж тривалості імпульсу.
     *
     * @param channel Ідентифікатор апаратного каналу ШІМ/таймера
     * @param minPulseUs Нижній безпечний поріг тривалості імпульсу (мкс)
     * @param maxPulseUs Верхній безпечний поріг тривалості імпульсу (мкс)
     * @return true при успішному конфігуруванні, false при невалідних межах
     */
    bool init(uint8_t channel, uint16_t minPulseUs = DEFAULT_MIN_PULSE_US, uint16_t maxPulseUs = DEFAULT_MAX_PULSE_US);

    /**
     * @brief Задання кута повороту вала сервоприводу.
     *
     * @param angleDeg Бажаний кут повороту у градусах (0.0 .. 180.0°)
     * @return DriverStatus Результат обробки команди
     */
    DriverStatus setAngle(float angleDeg);

    /**
     * @brief Пряме завдання тривалості ШІМ-імпульсу у мікросекундах.
     *
     * @param pulseUs Тривалість позитивного імпульсу (мкс)
     * @return DriverStatus Результат обробки команди з перевіркою безпечних меж
     */
    DriverStatus setPulseWidthUs(uint16_t pulseUs);

    /**
     * @brief Отримання поточного значення тривалості імпульсу у мікросекундах.
     */
    uint16_t getPulseWidthUs() const { return m_currentPulseUs; }

    /**
     * @brief Отримання поточного розрахованого кута повороту вала.
     */
    float getAngleDeg() const { return m_currentAngleDeg; }

    /**
     * @brief Перетворення тривалості імпульсу (мкс) у відліки регістру апаратного таймера.
     */
    uint32_t pulseToTimerTicks(uint16_t pulseUs) const;

    /**
     * @brief Увімкнення або вимкнення виходу ШІМ-сигналу.
     */
    void enableOutput(bool enable);

    /**
     * @brief Перевірка активності виходу ШІМ.
     */
    bool isOutputEnabled() const { return m_enabled; }

    /**
     * @brief Перевірка, чи входить задана тривалість імпульсу у встановлені безпечні межі.
     */
    bool isPulseValid(uint16_t pulseUs) const;

    uint16_t getMinPulseUs() const { return m_minPulseUs; }
    uint16_t getMaxPulseUs() const { return m_maxPulseUs; }

private:
    uint8_t m_channel{0};
    uint16_t m_minPulseUs{DEFAULT_MIN_PULSE_US};
    uint16_t m_maxPulseUs{DEFAULT_MAX_PULSE_US};
    uint16_t m_currentPulseUs{1500};
    float m_currentAngleDeg{90.0f};
    bool m_enabled{false};

    /**
     * @brief Симуляція оновлення системного регістру порівняння таймера (Compare Register).
     */
    void updateHardwareRegisters(uint32_t ticks);
};

} // namespace rc_servo

#endif // SERVO_DRIVER_HPP
