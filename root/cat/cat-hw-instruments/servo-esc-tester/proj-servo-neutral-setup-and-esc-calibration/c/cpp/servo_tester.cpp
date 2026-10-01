#include "servo_tester.hpp"
#include <algorithm>

namespace {
    static uint16_t g_simulatedAdcRaw = 512;
    static uint16_t g_hardwarePwmCompareUs = ServoTester::NeutralPulseUs;
}

ServoTester::ServoTester() {
    setPulseUs(NeutralPulseUs);
}

void ServoTester::initHardware() {
    g_hardwarePwmCompareUs = NeutralPulseUs;
}

void ServoTester::setPulseUs(uint16_t pulseUs) {
    m_pulseWidthUs = std::clamp(pulseUs, MinPulseUs, MaxPulseUs);
    g_hardwarePwmCompareUs = m_pulseWidthUs;
}

uint16_t ServoTester::readAdcPulse() {
    uint32_t pulse = MinPulseUs + (static_cast<uint32_t>(g_simulatedAdcRaw) * (MaxPulseUs - MinPulseUs)) / 1023;
    return static_cast<uint16_t>(pulse);
}

void ServoTester::nextMode() {
    switch (m_mode) {
        case ServoMode::Manual:
            m_mode = ServoMode::Neutral;
            setPulseUs(NeutralPulseUs);
            break;
        case ServoMode::Neutral:
            m_mode = ServoMode::Sweep;
            break;
        case ServoMode::Sweep:
            m_mode = ServoMode::Manual;
            break;
    }
}

void ServoTester::update(uint32_t currentMs, bool buttonPressed) {
    constexpr uint32_t DebounceDelayMs = 50;
    constexpr uint32_t SweepIntervalMs = 15;
    constexpr uint16_t SweepStepUs = 10;

    if (buttonPressed != m_lastButtonState) {
        m_lastButtonMs = currentMs;
        m_lastButtonState = buttonPressed;
    }

    if (buttonPressed && (currentMs - m_lastButtonMs >= DebounceDelayMs)) {
        nextMode();
        m_lastButtonMs = currentMs + 200;
    }

    switch (m_mode) {
        case ServoMode::Manual:
            setPulseUs(readAdcPulse());
            break;
        case ServoMode::Neutral:
            setPulseUs(NeutralPulseUs);
            break;
        case ServoMode::Sweep:
            if (currentMs - m_lastSweepMs >= SweepIntervalMs) {
                m_lastSweepMs = currentMs;
                int32_t newPulse = static_cast<int32_t>(m_pulseWidthUs) + (m_sweepDir * SweepStepUs);
                
                if (newPulse >= MaxPulseUs) {
                    newPulse = MaxPulseUs;
                    m_sweepDir = -1;
                } else if (newPulse <= MinPulseUs) {
                    newPulse = MinPulseUs;
                    m_sweepDir = 1;
                }
                
                setPulseUs(static_cast<uint16_t>(newPulse));
            }
            break;
    }
}

void ServoTester::calibrateEsc() {
    setPulseUs(MaxPulseUs);
    setPulseUs(MinPulseUs);
    m_escCalibrated = true;
    m_mode = ServoMode::Manual;
}
