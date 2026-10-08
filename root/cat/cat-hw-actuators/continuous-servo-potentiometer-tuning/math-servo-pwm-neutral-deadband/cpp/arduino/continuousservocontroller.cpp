#include <Arduino.h>

constexpr uint16_t SERVO_PWM_NEUTRAL_US = 1500;
constexpr uint16_t SERVO_PWM_MIN_US     = 1000;
constexpr uint16_t SERVO_PWM_MAX_US     = 2000;

class ContinuousServoController {
private:
    uint16_t deadbandHalfUs;

public:
    explicit ContinuousServoController(uint16_t deadbandHalf = 16) 
        : deadbandHalfUs(deadbandHalf) {}

    uint16_t processPwmSignal(uint16_t tInUs) const {
        tInUs = constrain(tInUs, SERVO_PWM_MIN_US, SERVO_PWM_MAX_US);
        int32_t delta = static_cast<int32_t>(tInUs) - SERVO_PWM_NEUTRAL_US;

        if (abs(delta) <= static_cast<int32_t>(deadbandHalfUs)) {
            return SERVO_PWM_NEUTRAL_US;
        }

        int32_t maxSpan = SERVO_PWM_MAX_US - SERVO_PWM_NEUTRAL_US;
        int32_t activeSpan = maxSpan - static_cast<int32_t>(deadbandHalfUs);

        if (delta > 0) {
            return SERVO_PWM_NEUTRAL_US + ((delta - deadbandHalfUs) * maxSpan) / activeSpan;
        } else {
            return SERVO_PWM_NEUTRAL_US + ((delta + deadbandHalfUs) * maxSpan) / activeSpan;
        }
    }
};
