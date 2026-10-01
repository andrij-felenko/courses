#ifndef SERVO_TESTER_HPP
#define SERVO_TESTER_HPP

#include <cstdint>

enum class ServoMode {
    Manual = 0,
    Neutral = 1,
    Sweep = 2
};

class ServoTester {
public:
    static constexpr uint16_t MinPulseUs = 1000;
    static constexpr uint16_t MaxPulseUs = 2000;
    static constexpr uint16_t NeutralPulseUs = 1500;
    static constexpr uint32_t PwmPeriodUs = 20000;

    ServoTester();

    void initHardware();
    void setPulseUs(uint16_t pulseUs);
    uint16_t getPulseUs() const { return m_pulseWidthUs; }

    ServoMode getMode() const { return m_mode; }
    void nextMode();

    void update(uint32_t currentMs, bool buttonPressed);
    void calibrateEsc();

private:
    uint16_t readAdcPulse();

    ServoMode m_mode{ServoMode::Manual};
    uint16_t m_pulseWidthUs{NeutralPulseUs};
    int8_t m_sweepDir{1};
    uint32_t m_lastSweepMs{0};
    uint32_t m_lastButtonMs{0};
    bool m_lastButtonState{false};
    bool m_escCalibrated{false};
};

#endif // SERVO_TESTER_HPP
