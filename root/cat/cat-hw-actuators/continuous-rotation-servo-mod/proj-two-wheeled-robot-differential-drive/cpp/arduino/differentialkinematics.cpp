#include <Arduino.h>

class DifferentialKinematics {
private:
    float trackWidth;
    float kTrimLeft;
    float kTrimRight;

public:
    DifferentialKinematics(float b, float trimLeft = 1.0f, float trimRight = 1.0f)
        : trackWidth(b), kTrimLeft(trimLeft), kTrimRight(trimRight) {}

    void computeWheelSpeeds(float v, float omega, float &outSpeedLeft, float &outSpeedRight) const {
        float vL = v - (omega * trackWidth / 2.0f);
        float vR = v + (omega * trackWidth / 2.0f);

        outSpeedLeft  = vL * kTrimLeft;
        outSpeedRight = vR * kTrimRight;
    }
};
