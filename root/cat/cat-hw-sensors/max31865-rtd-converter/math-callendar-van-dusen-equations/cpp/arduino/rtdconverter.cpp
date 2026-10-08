#include <Arduino.h>
#include <cmath>

class RTDConverter {
public:
    static constexpr float R0 = 100.0f;
    static constexpr float A  = 3.9083e-3f;
    static constexpr float B  = -5.775e-7f;
    static constexpr float C  = -4.183e-12f;

    static float convertToTemperature(float rMeas) {
        float discr = A * A - 4.0f * B * (1.0f - rMeas / R0);
        if (discr < 0.0f) {
            return NAN;
        }

        float t = (-A + std::sqrt(discr)) / (2.0f * B);
        if (t >= 0.0f) {
            return t;
        }

        // Чисельне обернення методом Ньютона — Рафсона
        for (uint8_t iter = 0; iter < 3; ++iter) {
            float t2 = t * t;
            float t3 = t2 * t;
            float t4 = t3 * t;

            float fVal = R0 * (1.0f + A * t + B * t2 - 100.0f * C * t3 + C * t4) - rMeas;
            float fPrime = R0 * (A + 2.0f * B * t - 300.0f * C * t2 + 4.0f * C * t3);

            t -= fVal / fPrime;
        }

        return t;
    }
};
