#ifndef SERVO_TESTER_HPP
#define SERVO_TESTER_HPP

#include "servo_driver.hpp"
#include "motion_profile.hpp"

namespace rc_servo {

/**
 * @brief Режими роботи сервотестера.
 */
enum class TesterMode {
    Manual,    /*!< Ручне позиціонування вала за цільовим кутом */
    AutoSweep, /*!< Автоматичне безперервне сканування діапазону */
    Neutral    /*!< Утримання вала у точній нейтралі (90°, 1500 мкс) */
};

/**
 * @brief Стан системи безпеки та виявлення критичних збоїв.
 */
enum class SafetyState {
    Normal,                    /*!< Нормальний режим без відхилень */
    FaultPulseOutOfBounds,     /*!< Аварія: спроба видачі імпульсу поза часовими бар'єрами */
    FaultDriverError           /*!< Аварія: помилка апаратного драйвера */
};

/**
 * @brief Клас високорівневого модульного сервотестера з захисними бар'єрами.
 *
 * Інтегрує ServoDriver та MotionProfiler для виконання контрольних випробувань,
 * калібрування нейтралі та автоматизованого прогону сервоприводу.
 */
class ServoTester {
public:
    ServoTester(ServoDriver& driver, MotionProfiler& profiler);

    /**
     * @brief Встановлення режиму випробування.
     */
    void setMode(TesterMode mode);

    /**
     * @brief Отримання поточного режиму роботи.
     */
    TesterMode getMode() const { return m_mode; }

    /**
     * @brief Налаштування меж авторозгону для режиму AutoSweep.
     */
    void setSweepRange(float minAngleDeg, float maxAngleDeg);

    /**
     * @brief Задання цільової позиції у ручному режимі (Manual).
     */
    void setManualTarget(float angleDeg);

    /**
     * @brief Періодичний крок виконання логіки сервотестера.
     * @param dtSec Дискрет часу з попередньої ітерації (с)
     */
    void update(float dtSec);

    /**
     * @brief Отримання стану системи безпеки.
     */
    SafetyState getSafetyState() const { return m_safetyState; }

    /**
     * @brief Перевірка наявності активного аварійного відключення.
     */
    bool isFaulted() const { return m_safetyState != SafetyState::Normal; }

    /**
     * @brief Скидання аварійного стану та відновлення роботи після перевірки.
     */
    void resetFault();

private:
    ServoDriver& m_driver;
    MotionProfiler& m_profiler;
    TesterMode m_mode{TesterMode::Neutral};
    SafetyState m_safetyState{SafetyState::Normal};

    float m_sweepMinDeg{10.0f};
    float m_sweepMaxDeg{170.0f};
    float m_manualTargetDeg{90.0f};
    bool m_sweepDirectionUp{true};

    void processModeLogic(float dtSec);
    void validateSafety(uint16_t pulseUs);
};

} // namespace rc_servo

#endif // SERVO_TESTER_HPP
