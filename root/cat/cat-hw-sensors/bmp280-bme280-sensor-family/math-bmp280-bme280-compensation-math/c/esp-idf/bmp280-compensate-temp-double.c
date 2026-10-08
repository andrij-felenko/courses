#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint16_t dig_T1;
    int16_t  dig_T2;
    int16_t  dig_T3;
} bmp280_temp_calib_t;

// Обчислення t_fine та температури у форматі з плаваючою крапкою (float/double)
double bmp280_compensate_temp_double(int32_t adc_T, const bmp280_temp_calib_t *calib, int32_t *out_t_fine) {
    double var1 = (((double)adc_T) / 16384.0 - ((double)calib->dig_T1) / 1024.0) * ((double)calib->dig_T2);
    double var2 = ((((double)adc_T) / 131072.0 - ((double)calib->dig_T1) / 8192.0) *
                   (((double)adc_T) / 131072.0 - ((double)calib->dig_T1) / 8192.0)) * ((double)calib->dig_T3);
    
    *out_t_fine = (int32_t)(var1 + var2);
    return (var1 + var2) / 5120.0; // Температура в градусах Цельсія (°C)
}

// Обчислення t_fine та температури 32-бітовою цілочисельною арифметикою
int32_t bmp280_compensate_temp_int32(int32_t adc_T, const bmp280_temp_calib_t *calib, int32_t *out_t_fine) {
    int32_t var1 = ((((adc_T >> 3) - ((int32_t)calib->dig_T1 << 1))) * ((int32_t)calib->dig_T2)) >> 11;
    int32_t var2 = (((((adc_T >> 4) - ((int32_t)calib->dig_T1)) * ((adc_T >> 4) - ((int32_t)calib->dig_T1))) >> 12) *
                    ((int32_t)calib->dig_T3)) >> 14;
    
    *out_t_fine = var1 + var2;
    return (*out_t_fine * 5 + 128) >> 8; // Температура в 0.01 °C (2508 = 25.08 °C)
}
