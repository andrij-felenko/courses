#include "motion_profile.hpp"
#include <algorithm>
#include <cmath>

namespace rc_servo {

MotionProfiler::MotionProfiler()
    : m_currentAngle(90.0f),
      m_targetAngle(90.0f),
      m_currentVelocity(0.0f),
      m_maxVelocity(180.0f),
      m_maxAccel(720.0f) {}

MotionProfiler::MotionProfiler(float maxVelocityDegPerSec, float maxAccelDegPerSec2)
    : m_currentAngle(90.0f),
      m_targetAngle(90.0f),
      m_currentVelocity(0.0f),
      m_maxVelocity(maxVelocityDegPerSec),
      m_maxAccel(maxAccelDegPerSec2) {
    setLimits(maxVelocityDegPerSec, maxAccelDegPerSec2);
}

void MotionProfiler::setLimits(float maxVelocityDegPerSec, float maxAccelDegPerSec2) {
    m_maxVelocity = std::abs(maxVelocityDegPerSec);
    m_maxAccel = std::abs(maxAccelDegPerSec2);
}

void MotionProfiler::setTargetAngle(float targetDeg) {
    m_targetAngle = std::clamp(targetDeg, 0.0f, 180.0f);
}

float MotionProfiler::update(float dtSec) {
    if (dtSec <= 0.0f) {
        return m_currentAngle;
    }

    float distance = m_targetAngle - m_currentAngle;

    if (std::abs(distance) < 0.01f && std::abs(m_currentVelocity) < 0.01f) {
        m_currentAngle = m_targetAngle;
        m_currentVelocity = 0.0f;
        return m_currentAngle;
    }

    // Дистанція гальмування при поточному значенні швидкості
    float stoppingDistance = (m_currentVelocity * m_currentVelocity) / (2.0f * m_maxAccel);
    float direction = (distance > 0.0f) ? 1.0f : -1.0f;

    // Визначаємо, чи потрібно прискорюватися, чи розганятися/гальмувати
    if (std::abs(distance) <= stoppingDistance && (m_currentVelocity * direction) > 0.0f) {
        // Гальмування перед цільовою точкою
        m_currentVelocity -= direction * m_maxAccel * dtSec;
        if ((direction > 0.0f && m_currentVelocity < 0.0f) || (direction < 0.0f && m_currentVelocity > 0.0f)) {
            m_currentVelocity = 0.0f;
        }
    } else {
        // Розгін або рух із постійною швидкістю
        m_currentVelocity += direction * m_maxAccel * dtSec;
        m_currentVelocity = std::clamp(m_currentVelocity, -m_maxVelocity, m_maxVelocity);
    }

    // Оновлення поточної позиції
    m_currentAngle += m_currentVelocity * dtSec;

    // Запобігання перерегулюванню при переході через цільовий кут
    if ((direction > 0.0f && m_currentAngle >= m_targetAngle) ||
        (direction < 0.0f && m_currentAngle <= m_targetAngle)) {
        m_currentAngle = m_targetAngle;
        m_currentVelocity = 0.0f;
    }

    return m_currentAngle;
}

void MotionProfiler::reset(float currentAngleDeg) {
    m_currentAngle = std::clamp(currentAngleDeg, 0.0f, 180.0f);
    m_targetAngle = m_currentAngle;
    m_currentVelocity = 0.0f;
}

bool MotionProfiler::isTargetReached() const {
    return std::abs(m_targetAngle - m_currentAngle) < 0.05f && std::abs(m_currentVelocity) < 0.05f;
}

} // namespace rc_servo
