#include <Arduino.h>

class FlowMeter {
private:
    float kFactorPulsesPerLiter;
    float lastFlowRateLpm;
    unsigned long lastTimestampMs;
    float totalVolumeLiters;

public:
    FlowMeter(float kFactor) 
        : kFactorPulsesPerLiter(kFactor), lastFlowRateLpm(0.0f), lastTimestampMs(0), totalVolumeLiters(0.0f) {}

    void update(uint32_t pulseCount, unsigned long currentTimestampMs) {
        if (lastTimestampMs == 0) {
            lastTimestampMs = currentTimestampMs;
            return;
        }

        float dtSec = (float)(currentTimestampMs - lastTimestampMs) / 1000.0f;
        if (dtSec <= 0.0f) return;

        // Обчислення частоти імпульсів
        float frequencyHz = (float)pulseCount / dtSec;

        // Поточна миттєва витрата в л/хв
        float currentFlowRateLpm = (frequencyHz * 60.0f) / kFactorPulsesPerLiter;

        // Обчислення середньої витрати в л/с та приросту об'єму методом трапецій
        float currentFlowLps = currentFlowRateLpm / 60.0f;
        float lastFlowLps = lastFlowRateLpm / 60.0f;
        float deltaVolumeLiters = ((lastFlowLps + currentFlowLps) / 2.0f) * dtSec;

        totalVolumeLiters += deltaVolumeLiters;
        lastFlowRateLpm = currentFlowRateLpm;
        lastTimestampMs = currentTimestampMs;
    }

    float getFlowRateLpm() const { return lastFlowRateLpm; }
    float getTotalVolumeLiters() const { return totalVolumeLiters; }
};
