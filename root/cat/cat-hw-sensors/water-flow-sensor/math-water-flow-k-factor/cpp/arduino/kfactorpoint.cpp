#include <Arduino.h>
#include <array>

struct KFactorPoint {
    float freqHz;
    float kFactor;
};

template <size_t N>
float getCorrectedKFactor(float freqHz, const std::array<KFactorPoint, N>& lut) {
    static_assert(N > 0, "Lookup table must not be empty");

    if (freqHz <= lut.front().freqHz) {
        return lut.front().kFactor;
    }
    if (freqHz >= lut.back().freqHz) {
        return lut.back().kFactor;
    }

    for (size_t i = 0; i < N - 1; ++i) {
        if (freqHz >= lut[i].freqHz && freqHz <= lut[i + 1].freqHz) {
            float deltaF = lut[i + 1].freqHz - lut[i].freqHz;
            if (deltaF <= 0.0f) {
                return lut[i].kFactor;
            }
            float weight = (freqHz - lut[i].freqHz) / deltaF;
            return lut[i].kFactor + weight * (lut[i + 1].kFactor - lut[i].kFactor);
        }
    }
    return lut.back().kFactor;
}
