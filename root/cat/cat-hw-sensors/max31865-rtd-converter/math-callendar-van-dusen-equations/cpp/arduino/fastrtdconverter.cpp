#include <Arduino.h>

class FastRTDConverter {
private:
    static constexpr int START_TEMP = -50;
    static constexpr int STEP_TEMP  = 10;
    static constexpr size_t LUT_SIZE = 11;

    static constexpr float LUT[LUT_SIZE] = {
        80.31f, 84.27f, 88.22f, 92.16f, 96.09f,
        100.00f, 103.90f, 107.79f, 111.67f, 115.54f, 119.40f
    };

public:
    static float interpolateTemperature(float rMeas) {
        if (rMeas <= LUT[0]) return static_cast<float>(START_TEMP);
        if (rMeas >= LUT[LUT_SIZE - 1]) return static_cast<float>(START_TEMP + (LUT_SIZE - 1) * STEP_TEMP);

        size_t idx = 0;
        while (idx < LUT_SIZE - 1 && rMeas > LUT[idx + 1]) {
            idx++;
        }

        float rLow = LUT[idx];
        float rHigh = LUT[idx + 1];
        float tLow = START_TEMP + idx * STEP_TEMP;

        return tLow + static_cast<float>(STEP_TEMP) * (rMeas - rLow) / (rHigh - rLow);
    }
};
