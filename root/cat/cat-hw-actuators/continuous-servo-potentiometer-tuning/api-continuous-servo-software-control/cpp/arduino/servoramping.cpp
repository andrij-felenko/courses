#include <Arduino.h>

class ServoRamping {
private:
    float currentPulseUs;
    float targetPulseUs;
    float maxChangePerStep;
    unsigned long lastUpdateMs;

public:
    ServoRamping(float initialPulseUs = 1500.0f) 
        : currentPulseUs(initialPulseUs), targetPulseUs(initialPulseUs), 
          maxChangePerStep(10.0f), lastUpdateMs(0) {}

    void setTargetPulse(float targetUs) {
        targetPulseUs = targetUs;
    }

    void setRampTime(float rampTimeSec, float updateIntervalMs = 20.0f) {
        float stepsCount = (rampTimeSec * 1000.0f) / updateIntervalMs;
        maxChangePerStep = 500.0f / stepsCount;
    }

    uint16_t update(unsigned long nowMs) {
        if (nowMs - lastUpdateMs >= 20) { // Оновлення кожні 20 мс (50 Гц)
            lastUpdateMs = nowMs;
            float diff = targetPulseUs - currentPulseUs;
            if (fabsf(diff) <= maxChangePerStep) {
                currentPulseUs = targetPulseUs;
            } else {
                currentPulseUs += (diff > 0.0f ? maxChangePerStep : -maxChangePerStep);
            }
        }
        return static_cast<uint16_t>(lroundf(currentPulseUs));
    }
};
