#include <Arduino.h>

class Pt100LutLinearizer {
public:
    static constexpr float START_TEMP = 0.0f;
    static constexpr float STEP_TEMP  = 10.0f;
    static constexpr size_t LUT_SIZE  = 11;

    // Швидка обробка виміряного опору через LUT та відрізково-лінійну інтерполяцію
    static float toCelsius(float rMeasured) noexcept {
        if (rMeasured <= LUT[0]) {
            return START_TEMP;
        }
        if (rMeasured >= LUT[LUT_SIZE - 1]) {
            return START_TEMP + static_cast<float>(LUT_SIZE - 1) * STEP_TEMP;
        }

        size_t i = 0;
        while (i < LUT_SIZE - 2 && LUT[i + 1] <= rMeasured) {
            i++;
        }

        const float rLow = LUT[i];
        const float rHigh = LUT[i + 1];
        const float tLow = START_TEMP + static_cast<float>(i) * STEP_TEMP;

        return tLow + (rMeasured - rLow) * STEP_TEMP / (rHigh - rLow);
    }

private:
    static constexpr float LUT[LUT_SIZE] = {
        100.00f, 103.90f, 107.79f, 111.67f, 115.54f,
        119.40f, 123.24f, 127.08f, 130.90f, 134.71f, 138.51f
    };
};
