#include <Servo.h>

class ContinuousServo {
private:
    Servo servoDevice;
    int pinNumber;
    uint16_t neutralUs;
    uint16_t maxUsDelta;

public:
    ContinuousServo(int pin, uint16_t neutral = 1500, uint16_t delta = 500)
        : pinNumber(pin), neutralUs(neutral), maxUsDelta(delta) {}

    void begin() {
        servoDevice.attach(pinNumber);
        stop();
    }

    // speedPercent від -100 (макс. CCW) до +100 (макс. CW)
    void setSpeed(int8_t speedPercent) {
        if (speedPercent > 100) speedPercent = 100;
        if (speedPercent < -100) speedPercent = -100;

        uint16_t pulseUs = neutralUs + (int32_t)speedPercent * maxUsDelta / 100;
        servoDevice.writeMicroseconds(pulseUs);
    }

    void stop() {
        servoDevice.writeMicroseconds(neutralUs);
    }
};
