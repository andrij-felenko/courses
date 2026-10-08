#include <math.h>
#include <stdint.h>

#define AS5048_CPR           16384  // 14 біт роздільна здатність (Counts Per Revolution)
#define TWO_PI               6.283185307179586f

typedef struct {
    uint8_t pole_pairs;
    uint16_t zero_offset;
} bldc_foc_sensor_t;

// Обчислення електричного кута в радіанах [0, 2π)
float bldc_get_electrical_angle(bldc_foc_sensor_t *sensor, uint16_t raw_angle) {
    // 1. Програмний зсув нуля
    int32_t corrected = (int32_t)raw_angle - (int32_t)sensor->zero_offset;
    if (corrected < 0) {
        corrected += AS5048_CPR;
    }
    
    // 2. Нормалізація механічного кута від 0.0 до 1.0
    float mech_angle_norm = (float)corrected / (float)AS5048_CPR;
    
    // 3. Масштабування до електричних радіанів
    float elec_angle_rad = mech_angle_norm * (float)sensor->pole_pairs * TWO_PI;
    
    // 4. Зведення до діапазону [0, 2π)
    elec_angle_rad = fmodf(elec_angle_rad, TWO_PI);
    if (elec_angle_rad < 0.0f) {
        elec_angle_rad += TWO_PI;
    }
    
    return elec_angle_rad;
}
