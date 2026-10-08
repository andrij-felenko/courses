#include "servo_tester.hpp"
#include <algorithm>

namespace rc_servo {

ServoTester::ServoTester(ServoDriver& driver, MotionProfiler& profiler)
    : m_driver(driver),
      m_profiler(profiler),
      m_mode(TesterMode::Neutral),
      m_safetyState(SafetyState::Normal),
      m_sweepMinDeg(10.0f),
      m_sweepMaxDeg(170.0f),
      m_manualTargetDeg(90.0f),
      m_sweepDirectionUp(true) {
    m_profiler.reset(m_driver.getAngleDeg());
}

void ServoTester::setMode(TesterMode mode) {
    m_mode = mode;

    if (m_mode == TesterMode::Neutral) {
        m_profiler.setTargetAngle(90.0f);
    } else if (m_mode == TesterMode::Manual) {
        m_profiler.setTargetAngle(m_manualTargetDeg);
    } else if (m_mode == TesterMode::AutoSweep) {
        m_sweepDirectionUp = true;
        m_profiler.setTargetAngle(m_sweepMaxDeg);
    }
}

void ServoTester::setSweepRange(float minAngleDeg, float maxAngleDeg) {
    m_sweepMinDeg = std::clamp(minAngleDeg, 0.0f, 180.0f);
    m_sweepMaxDeg = std::clamp(maxAngleDeg, 0.0f, 180.0f);

    if (m_sweepMinDeg > m_sweepMaxDeg) {
        std::swap(m_sweepMinDeg, m_sweepMaxDeg);
    }
}

void ServoTester::setManualTarget(float angleDeg) {
    m_manualTargetDeg = std::clamp(angleDeg, 0.0f, 180.0f);
    if (m_mode == TesterMode::Manual) {
        m_profiler.setTargetAngle(m_manualTargetDeg);
    }
}

void ServoTester::update(float dtSec) {
    if (isFaulted()) {
        // У разі спрацювання захисту примусово знімаємо ШІМ-сигнал
        m_driver.enableOutput(false);
        return;
    }

    processModeLogic(dtSec);

    // Розраховуємо нову точку плавної траєкторії
    float calculatedAngle = m_profiler.update(dtSec);

    // Передаємо значення драйверу та перевіряємо статус
    DriverStatus status = m_driver.setAngle(calculatedAngle);
    if (status != DriverStatus::Ok) {
        m_safetyState = SafetyState::FaultDriverError;
        m_driver.enableOutput(false);
        return;
    }

    // Додаткова захисна валідація тривалості сформованого імпульсу
    validateSafety(m_driver.getPulseWidthUs());
}

void ServoTester::processModeLogic(float dtSec) {
    (void)dtSec;

    switch (m_mode) {
        case TesterMode::Neutral:
            m_profiler.setTargetAngle(90.0f);
            break;

        case TesterMode::Manual:
            m_profiler.setTargetAngle(m_manualTargetDeg);
            break;

        case TesterMode::AutoSweep:
            if (m_profiler.isTargetReached()) {
                if (m_sweepDirectionUp) {
                    m_sweepDirectionUp = false;
                    m_profiler.setTargetAngle(m_sweepMinDeg);
                } else {
                    m_sweepDirectionUp = true;
                    m_profiler.setTargetAngle(m_sweepMaxDeg);
                }
            }
            break;
    }
}

void ServoTester::validateSafety(uint16_t pulseUs) {
    // Аварійні часові бар'єри (450 мкс .. 2550 мкс). 
    // Вихід за ці межі свідчить про програмний збій або пошкодження даних,
    // що викликає заклинювання та термічне пошкодження обмоток двигуна.
    constexpr uint16_t HARD_MIN_PULSE_LIMIT_US = 450;
    constexpr uint16_t HARD_MAX_PULSE_LIMIT_US = 2550;

    if (pulseUs < HARD_MIN_PULSE_LIMIT_US || pulseUs > HARD_MAX_PULSE_LIMIT_US) {
        m_safetyState = SafetyState::FaultPulseOutOfBounds;
        m_driver.enableOutput(false);
    }
}

void ServoTester::resetFault() {
    m_safetyState = SafetyState::Normal;
    m_profiler.reset(90.0f);
    m_driver.init(0, m_driver.getMinPulseUs(), m_driver.getMaxPulseUs());
    m_driver.enableOutput(true);
    setMode(TesterMode::Neutral);
}

} // namespace rc_servo
