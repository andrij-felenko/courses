#include <Arduino.h>

struct Acceleration {
    float x;
    float y;
    float z;
};

constexpr float ADXL345_SCALE_FACTOR_G = 0.0039f;
constexpr float GRAVITY_EARTH = 9.80665f;

Acceleration convertRawToAcceleration(int16_t rawX, int16_t rawY, int16_t rawZ) {
    return {
        static_cast<float>(rawX) * ADXL345_SCALE_FACTOR_G * GRAVITY_EARTH,
        static_cast<float>(rawY) * ADXL345_SCALE_FACTOR_G * GRAVITY_EARTH,
        static_cast<float>(rawZ) * ADXL345_SCALE_FACTOR_G * GRAVITY_EARTH
    };
}
