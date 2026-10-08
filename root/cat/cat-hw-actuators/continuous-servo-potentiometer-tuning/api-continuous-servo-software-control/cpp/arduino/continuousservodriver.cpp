#include <Arduino.h>
#include <Servo.h>

class ContinuousServoDriver {
private:
    Servo servoDevice;
    uint8_t signalPin;
    int16_t offsetUs;
    uint16_t deadbandUs;
    float currentPulse;
    float targetPulse;
    float rampStepUs;
    unsigned long lastStepMs;

    uint16_t clampPulse(float pulse) {
        if (pulse < 500.0f) return 500;
        if (pulse > 2500.0f) return 2500;
        return static_cast<uint16_t>(lroundf(pulse));
    }

public:
    ContinuousServoDriver() 
        : signalPin(255), offsetUs(0), deadbandUs(12), 
          currentPulse(1500.0f), targetPulse(1500.0f), 
          rampStepUs(25.0f), lastStepMs(0) {}

    bool attach(uint8_t pin) {
        signalPin = pin;
        currentPulse = 1500.0f + offsetUs;
        targetPulse = currentPulse;
        return servoDevice.attach(signalPin) != 0;
    }

    void setCalibration(int16_t offset, uint16_t deadband) {
        offsetUs = offset;
        deadbandUs = deadband;
    }

    void setSpeed(float speed) {
        if (speed > 1.0f) speed = 1.0f;
        if (speed < -1.0f) speed = -1.0f;

        float absS = fabsf(speed);
        float dbNorm = static_cast<float>(deadbandUs) / 500.0f;

        if (absS <= dbNorm) {
            targetPulse = 1500.0f + offsetUs;
            return;
        }

        float scaledS = (absS - dbNorm) / (1.0f - dbNorm);
        if (speed < 0.0f) scaledS = -scaledS;

        targetPulse = (1500.0f + offsetUs) + (scaledS * 500.0f);
    }

    void update(unsigned long nowMs) {
        if (nowMs - lastStepMs < 20) return;
        lastStepMs = nowMs;

        float diff = targetPulse - currentPulse;
        if (fabsf(diff) <= rampStepUs) {
            currentPulse = targetPulse;
        } else {
            currentPulse += (diff > 0.0f) ? rampStepUs : -rampStepUs;
        }

        servoDevice.writeMicroseconds(clampPulse(currentPulse));
    }

    void stop() {
        targetPulse = 1500.0f + offsetUs;
        currentPulse = targetPulse;
        servoDevice.writeMicroseconds(clampPulse(currentPulse));
    }
};
