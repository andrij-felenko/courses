#include "servo_driver.hpp"
#include <algorithm>
#include <cmath>

namespace rc_servo {

ServoDriver::ServoDriver()
    : m_channel(0),
      m_minPulseUs(DEFAULT_MIN_PULSE_US),
      m_maxPulseUs(DEFAULT_MAX_PULSE_US),
      m_currentPulseUs(1500),
      m_currentAngleDeg(90.0f),
      m_enabled(false) {}

ServoDriver::ServoDriver(uint8_t channel, uint16_t minPulseUs, uint16_t maxPulseUs)
    : m_channel(channel),
      m_minPulseUs(minPulseUs),
      m_maxPulseUs(maxPulseUs),
      m_currentPulseUs(1500),
      m_currentAngleDeg(90.0f),
      m_enabled(false) {
    init(channel, minPulseUs, maxPulseUs);
}

bool ServoDriver::init(uint8_t channel, uint16_t minPulseUs, uint16_t maxPulseUs) {
    if (minPulseUs >= maxPulseUs || minPulseUs < 300 || maxPulseUs > 3000) {
        return false;
    }

    m_channel = channel;
    m_minPulseUs = minPulseUs;
    m_maxPulseUs = maxPulseUs;
    m_currentPulseUs = (minPulseUs + maxPulseUs) / 2;
    m_currentAngleDeg = 90.0f;
    m_enabled = false;

    uint32_t initialTicks = pulseToTimerTicks(m_currentPulseUs);
    updateHardwareRegisters(initialTicks);

    return true;
}

DriverStatus ServoDriver::setAngle(float angleDeg) {
    if (!m_enabled) {
        return DriverStatus::ErrDisabled;
    }

    if (angleDeg < MIN_ANGLE_DEG || angleDeg > MAX_ANGLE_DEG) {
        return DriverStatus::ErrAngleOutOfBounds;
    }

    // Пропорційне мапування кута 0..180° у діапазон тривалості імпульсу [minPulseUs..maxPulseUs]
    float normalized = (angleDeg - MIN_ANGLE_DEG) / (MAX_ANGLE_DEG - MIN_ANGLE_DEG);
    uint16_t pulseUs = static_cast<uint16_t>(m_minPulseUs + normalized * (m_maxPulseUs - m_minPulseUs));

    return setPulseWidthUs(pulseUs);
}

DriverStatus ServoDriver::setPulseWidthUs(uint16_t pulseUs) {
    if (!m_enabled) {
        return DriverStatus::ErrDisabled;
    }

    if (!isPulseValid(pulseUs)) {
        return DriverStatus::ErrPulseWidthOutOfBounds;
    }

    m_currentPulseUs = pulseUs;

    // Обчислення зворотної відповідності кута для контролю стану
    float normalized = static_cast<float>(pulseUs - m_minPulseUs) / static_cast<float>(m_maxPulseUs - m_minPulseUs);
    m_currentAngleDeg = MIN_ANGLE_DEG + normalized * (MAX_ANGLE_DEG - MIN_ANGLE_DEG);

    uint32_t ticks = pulseToTimerTicks(m_currentPulseUs);
    updateHardwareRegisters(ticks);

    return DriverStatus::Ok;
}

uint32_t ServoDriver::pulseToTimerTicks(uint16_t pulseUs) const {
    // 1 секунда = 1,000,000 мкс. 
    // За частоти тактування 2 МГц: 1 мкс = 2 такти таймера.
    return (static_cast<uint64_t>(pulseUs) * TIMER_CLOCK_HZ) / 1000000UL;
}

void ServoDriver::enableOutput(bool enable) {
    m_enabled = enable;
    if (!enable) {
        // При вимкненні скидаємо регістр порівняння у 0 для припинення генерації імпульсу
        updateHardwareRegisters(0);
    } else {
        // При повторній активації поновлюємо вихідний ШІМ-сигнал
        uint32_t ticks = pulseToTimerTicks(m_currentPulseUs);
        updateHardwareRegisters(ticks);
    }
}

bool ServoDriver::isPulseValid(uint16_t pulseUs) const {
    return (pulseUs >= m_minPulseUs && pulseUs <= m_maxPulseUs);
}

void ServoDriver::updateHardwareRegisters(uint32_t ticks) {
    // Симуляція запису значення у регістр порівняння таймера (наприклад, TIMx->CCR1 / OCR1A)
    (void)ticks;
}

} // namespace rc_servo
