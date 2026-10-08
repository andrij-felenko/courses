#include <Arduino.h>

class RtdConverter {
public:
    static constexpr float R0 = 100.0f;
    static constexpr float A  = 3.9083e-3f;
    static constexpr float B  = -5.775e-7f;
    static constexpr float C  = -4.183e-12f;

    // Швидкий розрахунок температури з використанням float та 2 ітерацій Ньютона
    static float readTemperature(float resistance) {
        float Z1 = -A;
        float Z2 = A * A - (4.0f * B * (1.0f - resistance / R0));
        float temp = (Z1 + sqrtf(Z2)) / (2.0f * B);

        if (resistance < R0) {
            for (uint8_t i = 0; i < 2; ++i) {
                float t2 = temp * temp;
                float t3 = t2 * temp;
                float f = R0 * (1.0f + A * temp + B * t2 + C * (temp - 100.0f) * t3) - resistance;
                float f_prime = R0 * (A + 2.0f * B * temp - 300.0f * C * t2 + 4.0f * C * t3);
                temp -= f / f_prime;
            }
        }
        return temp;
    }
};
