// Калібрування та масштабування давачів кута положення в C (ESP-IDF)
#include <stdio.h>
#include <stdint.h>
#include <math.h>

typedef struct {
    uint16_t adc_min;     // Мінімальний відлік АЦП на краю діапазону
    uint16_t adc_max;     // Максимальний відлік АЦП
    float angle_min;      // Кут при adc_min (наприклад, 0.0 градусів)
    float angle_max;      // Кут при adc_max (наприклад, 180.0 градусів)
    uint16_t zero_offset; // Зсув нульової точки АЦП
} pot_calibration_t;

// Обчислення каліброваного кута потенціометра з лінійною інтерполяцією та обмеженням
float calculate_potentiometer_angle(uint16_t raw_adc, const pot_calibration_t *cal) {
    // Обмеження вхідного значення в межах діапазону калібрування
    if (raw_adc < cal->adc_min) raw_adc = cal->adc_min;
    if (raw_adc > cal->adc_max) raw_adc = cal->adc_max;

    // Врахування зсуву нуля
    int32_t corrected_adc = (int32_t)raw_adc - cal->zero_offset;
    if (corrected_adc < (int32_t)cal->adc_min) corrected_adc = cal->adc_min;

    float k_scale = (cal->angle_max - cal->angle_min) / (float)(cal->adc_max - cal->adc_min);
    return cal->angle_min + ((float)corrected_adc - (float)cal->adc_min) * k_scale;
}

// Калібрування нульової точки 14-бітного магнітного енкодера з прив'язкою до 0..360 градусів
float calculate_magnetic_encoder_angle(uint16_t raw_angle_14bit, uint16_t zero_offset_14bit) {
    int32_t diff = (int32_t)raw_angle_14bit - (int32_t)zero_offset_14bit;
    if (diff < 0) {
        diff += 16384; // Обробка кільцевого переходу через 360 градусів
    }
    uint16_t corrected_raw = (uint16_t)(diff & 0x3FFF);
    return ((float)corrected_raw * 360.0f) / 16384.0f;
}
