#include <cstdint>
#include <cmath>
#include <algorithm>

class OV2640GainCalculator {
public:
    static uint8_t computeRegister(float targetGain) {
        if (targetGain <= 1.0f) return 0x00;
        if (targetGain >= 32.0f) return 0xFF;

        uint8_t regVal = 0;
        float g = targetGain;

        const struct { uint8_t bit; float factor; } stages[] = {
            {7, 2.0f},
            {6, 1.5f},
            {5, 1.25f},
            {4, 1.125f}
        };

        for (const auto& stage : stages) {
            if (g >= stage.factor) {
                regVal |= (1 << stage.bit);
                g /= stage.factor;
            }
        }

        int step = static_cast<int>(std::round((g - 1.0f) * 16.0f));
        step = std::clamp(step, 0, 15);

        return regVal | static_cast<uint8_t>(step);
    }
};
