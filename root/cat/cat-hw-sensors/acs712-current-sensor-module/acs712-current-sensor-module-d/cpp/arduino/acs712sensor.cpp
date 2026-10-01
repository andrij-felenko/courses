#include <Arduino.h>
#include <cmath>

class ACS712Sensor {
private:
    float sensitivity;
    uint16_t zeroAdc;
    uint16_t adcMax;
    float vref;

public:
    ACS712Sensor(float sens, uint16_t zero = 512, uint16_t maxAdc = 1023, float v = 5.0f)
        : sensitivity(sens), zeroAdc(zero), adcMax(maxAdc), vref(v) {}

    float calculateDC(uint16_t adcRaw) const {
        float voltageDiff = (static_cast<float>(adcRaw) - zeroAdc) * vref / adcMax;
        return voltageDiff / sensitivity;
    }

    float calculateRMS(const uint16_t* samples, size_t count) const {
        if (count == 0) return 0.0f;
        float sumSq = 0.0f;
        for (size_t i = 0; i < count; ++i) {
            float iVal = calculateDC(samples[i]);
            sumSq += iVal * iVal;
        }
        return std::sqrt(sumSq / static_cast<float>(count));
    }
};
