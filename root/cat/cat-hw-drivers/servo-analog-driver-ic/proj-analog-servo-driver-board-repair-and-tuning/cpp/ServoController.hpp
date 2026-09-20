#ifndef SERVO_CONTROLLER_HPP
#define SERVO_CONTROLLER_HPP

#include <cstdint>

namespace servo {

/// Конфігурація часових параметрів імпульсу керування (у мікросекундах).
/// Призначена для адаптації під мікросхеми сервопідсилювачів AA5188 та KC0032.
struct PulseConfig {
    uint16_t minPulseUs{1000};    ///< Мінімальна тривалість імпульсу (зазвичай 1000 мкс / 0°)
    uint16_t maxPulseUs{2000};    ///< Максимальна тривалість імпульсу (зазвичай 2000 мкс / 180°)
    uint16_t centerPulseUs{1500}; ///< Нейтральне положення (1500 мкс / 90°)
    uint16_t framePeriodUs{20000};///< Період фрейму ШІМ (20000 мкс = 50 Гц)
};

/// Налаштування зони нечутливості (deadband) для придушення осциляцій та нагріву силових ключів.
struct DeadbandConfig {
    uint16_t deadbandUs{4}; ///< Поріг зони нечутливості у мікросекундах (типово 2–5 мкс для AA5188/KC0032)
    bool enabled{true};     ///< Прапорець активації відсікання дрібних флуктуацій
};

/// Структура опису обчисленого часового таймінгу ШІМ для периферійного таймера МК.
struct TimerTiming {
    uint32_t pulseDurationUs; ///< Активна тривалість імпульсу в мкс
    uint32_t periodUs;        ///< Повний період фрейму в мкс
    float dutyCyclePercent;   ///< Коефіцієнт заповнення ШІМ у відсотках (0.0 - 100.0%)
    uint32_t timerTicks;      ///< Кількість тіків таймера для заданої частоти тактування
};

/// Специфічні типи мікросхем аналогових сервопідсилювачів
enum class ServoChipType {
    AA5188, ///< Стандартний аналоговий сервопідсилювач (зона нечутливості ~4 мкс)
    KC0032  ///< Прецизійний аналоговий сервопідсилювач (зона нечутливості ~2 мкс)
};

/**
 * @class ServoController
 * @brief Клас для керування спеціалізованими аналоговими сервопідсилювачами AA5188 та KC0032.
 *
 * Перетворює цільові кутові значення (у градусах) або відсотки у тривалість імпульсів із мікросекундною
 * точністю. Використовує алгоритм відсікання шумів зони нечутливості (deadband) для запобігання
 * мікроосциляціям двигуна та перегріву силових H-мостів драйвера.
 */
class ServoController {
public:
    /**
     * @brief Конструктор із вказанням типу мікросхеми сервопідсилювача.
     * @param chip Тип сервопідсилювача (AA5188 або KC0032).
     */
    explicit ServoController(ServoChipType chip = ServoChipType::AA5188);

    /**
     * @brief Налаштування часових діапазонів імпульсу та параметрів зони нечутливості.
     * @param pulseCfg Структура з конфігурацією імпульсів.
     * @param deadbandCfg Структура з параметрами deadband.
     * @return true у разі успішної перевірки параметрів, false якщо параметри некоректні.
     */
    bool configure(const PulseConfig& pulseCfg, const DeadbandConfig& deadbandCfg);

    /**
     * @brief Встановлення цільового кута позиціонування у градусах.
     * @param angleDeg Кут у градусах (0..maxAngleDeg).
     * @param maxAngleDeg Максимальний робочий кут (за замовчуванням 180.0°).
     * @return Вихідна тривалість імпульсу у мікросекундах після фільтрації.
     */
    uint16_t setTargetAngle(float angleDeg, float maxAngleDeg = 180.0f);

    /**
     * @brief Встановлення цільової тривалості імпульсу в мікросекундах.
     * @param targetUs Запитувана тривалість у мкс.
     * @return Результуюча тривалість імпульсу з урахуванням deadband.
     */
    uint16_t setTargetPulseUs(uint16_t targetUs);

    /**
     * @brief Отримання поточного вихідного імпульсу в мікросекундах.
     */
    uint16_t getCurrentPulseUs() const;

    /**
     * @brief Розрахунок параметрів для регістрів ШІМ-таймера мікроконтролера.
     * @param timerClockHz Частота тактування таймера (наприклад, 1000000 Гц = 1 МГц).
     * @return Обчислена структура TimerTiming.
     */
    TimerTiming calculateTimerTiming(uint32_t timerClockHz) const;

    /**
     * @brief Отримання поточних налаштувань зони нечутливості.
     */
    const DeadbandConfig& getDeadbandConfig() const;

    /**
     * @brief Отримання поточних параметрів тривалості імпульсу.
     */
    const PulseConfig& getPulseConfig() const;

    /**
     * @brief Динамічна зміна порогу зони нечутливості (мкс).
     * @param deadbandUs Нове значення порогу в мікросекундах.
     */
    void setDeadbandUs(uint16_t deadbandUs);

    /**
     * @brief Перевірка, чи була остання команда відфільтрована зоною нечутливості.
     */
    bool wasFilteredByDeadband() const;

private:
    ServoChipType m_chipType;
    PulseConfig m_pulseConfig;
    DeadbandConfig m_deadbandConfig;
    uint16_t m_currentPulseUs;
    bool m_lastActionFiltered{false};

    /**
     * @brief Внутрішній метод фільтрації тривалості імпульсу через deadband.
     */
    uint16_t filterDeadband(uint16_t targetUs);
};

} // namespace servo

#endif // SERVO_CONTROLLER_HPP
