#include <stdint.h>
#include <stdbool.h>

// Коефіцієнт масштабування у режимі Full Resolution (3.9 мг/МЗР або 0.0039 g/LSB)
#define ADXL345_SCALE_FACTOR_G 0.0039f
#define GRAVITY_EARTH 9.80665f

typedef struct {
    float x;
    float y;
    float z;
} acceleration_t;

acceleration_t convert_raw_to_acceleration(int16_t raw_x, int16_t raw_y, int16_t raw_z) {
    acceleration_t accel;
    // Множення сирого 16-бітного коду на постійний коефіцієнт масштабування
    accel.x = (float)raw_x * ADXL345_SCALE_FACTOR_G * GRAVITY_EARTH;
    accel.y = (float)raw_y * ADXL345_SCALE_FACTOR_G * GRAVITY_EARTH;
    accel.z = (float)raw_z * ADXL345_SCALE_FACTOR_G * GRAVITY_EARTH;
    return accel;
}
