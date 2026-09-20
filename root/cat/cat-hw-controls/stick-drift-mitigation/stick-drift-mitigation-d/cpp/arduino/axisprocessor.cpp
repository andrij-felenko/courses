#include <Arduino.h>

class AxisProcessor {
private:
    int16_t adcMin;
    int16_t adcCenter;
    int16_t adcMax;
    float deadzone;
    float emaAlpha;
    float filteredVal;

public:
    AxisProcessor(int16_t minV, int16_t centerV, int16_t maxV)
        : adcMin(minV), adcCenter(centerV), adcMax(maxV),
          deadzone(0.08f), emaAlpha(0.2f), filteredVal(static_cast<float>(centerV)) {}

    float process(int16_t rawAdc) {
        // 1. Фільтрація EMA
        filteredVal += emaAlpha * (static_cast<float>(rawAdc) - filteredVal);

        // 2. Двохсегментне мапування
        float norm = 0.0f;
        if (filteredVal < static_cast<float>(adcCenter)) {
            float span = static_cast<float>(adcCenter - adcMin);
            if (span > 1.0f) norm = (filteredVal - static_cast<float>(adcCenter)) / span;
        } else {
            float span = static_cast<float>(adcMax - adcCenter);
            if (span > 1.0f) norm = (filteredVal - static_cast<float>(adcCenter)) / span;
        }

        norm = constrain(norm, -1.0f, 1.0f);

        // 3. Масштабована мертва зона
        float absNorm = fabs(norm);
        if (absNorm < deadzone) {
            return 0.0f;
        }
        float sign = (norm > 0.0f) ? 1.0f : -1.0f;
        return sign * ((absNorm - deadzone) / (1.0f - deadzone));
    }
};
