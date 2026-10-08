#include <Arduino.h>
#include <math.h>

class RTDLinearizer {
private:
    static constexpr float R0 = 100.0f;
    static constexpr float A  = 3.9083e-3f;
    static constexpr float B  = -5.775e-7f;
    static constexpr float C  = -4.183e-12f;

public:
    static float calculateTemperature(float rMeas) {
        float discr = A * A - 4.0f * B * (1.0f - rMeas / R0);
        float t = (-A + sqrtf(discr)) / (2.0f * B);

        if (t >= 0.0f) {
            return t;
        }

        for (uint8_t iter = 0; iter < 3; ++iter) {
            float t2 = t * t;
            float t3 = t2 * t;
            float fVal = R0 * (1.0f + A * t + B * t2 + C * (t - 100.0f) * t3) - rMeas;
            float fDeriv = R0 * (A + 2.0f * B * t + 4.0f * C * t3 - 300.0f * C * t2);
            float step = fVal / fDeriv;
            t -= step;
            if (fabsf(step) < 0.0001f) {
                break;
            }
        }
        return t;
    }
};
