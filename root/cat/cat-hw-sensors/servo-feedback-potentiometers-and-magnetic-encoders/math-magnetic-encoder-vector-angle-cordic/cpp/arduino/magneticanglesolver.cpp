#include <Arduino.h>

class MagneticAngleSolver {
private:
    static const int NUM_ITERATIONS = 14;
    int16_t cordic_lut[16];

public:
    MagneticAngleSolver() {
        // Ініціалізація LUT кутів arctan(2^-i) для Q1.15
        for (int i = 0; i < NUM_ITERATIONS; i++) {
            cordic_lut[i] = (int16_t)(atan(pow(2.0, -i)) * 32768.0 / M_PI);
        }
    }

    // Повертає кут у радіанах від -PI до +PI
    float calculateAngle(float cos_val, float sin_val) {
        // Стандартний atan2 з квадрантною логікою для опрацювання межі
        if (cos_val == 0.0f && sin_val == 0.0f) {
            return 0.0f;
        }
        return atan2f(sin_val, cos_val);
    }
};
