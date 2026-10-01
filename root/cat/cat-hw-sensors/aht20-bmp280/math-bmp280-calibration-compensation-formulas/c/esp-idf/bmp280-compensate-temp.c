#include <stdint.h>

// Структура калібрувальних коефіцієнтів BMP280 з NVM
typedef struct {
    uint16_t dig_T1;
    int16_t  dig_T2;
    int16_t  dig_T3;
    uint16_t dig_P1;
    int16_t  dig_P2;
    int16_t  dig_P3;
    int16_t  dig_P4;
    int16_t  dig_P5;
    int16_t  dig_P6;
    int16_t  dig_P7;
    int16_t  dig_P8;
    int16_t  dig_P9;
} bmp280_calib_t;

// Обчислення температури у градусах Цельсія з отриманням t_fine
float bmp280_compensate_temp(int32_t adc_T, const bmp280_calib_t *calib, int32_t *t_fine) {
    int32_t var1 = ((((adc_T >> 3) - ((int32_t)calib->dig_T1 << 1))) * ((int32_t)calib->dig_T2)) >> 11;
    int32_t var2 = (((((adc_T >> 4) - ((int32_t)calib->dig_T1)) * ((adc_T >> 4) - ((int32_t)calib->dig_T1))) >> 12) * ((int32_t)calib->dig_T3)) >> 14;
    *t_fine = var1 + var2;
    return (*t_fine * 5 + 128) / 25600.0f;
}

// 64-бітне цілочисельне обчислення тиску в Паскалях
uint32_t bmp280_compensate_press_64bit(int32_t adc_P, const bmp280_calib_t *calib, int32_t t_fine) {
    int64_t var1 = ((int64_t)t_fine) - 128000;
    int64_t var2 = var1 * var1 * (int64_t)calib->dig_P6;
    var2 = var2 + ((var1 * (int64_t)calib->dig_P5) << 17);
    var2 = var2 + (((int64_t)calib->dig_P4) << 35);
    var1 = ((var1 * var1 * (int64_t)calib->dig_P3) >> 8) + ((var1 * (int64_t)calib->dig_P2) << 12);
    var1 = (((((int64_t)1) << 47) + var1)) * ((int64_t)calib->dig_P1) >> 33;

    if (var1 == 0) {
        return 0; // Запобігання діленню на нуль
    }

    int64_t p = 1048576 - adc_P;
    p = (((p << 31) - var2) * 3125) / var1;
    int64_t var1_p = (((int64_t)calib->dig_P9) * (p >> 13) * (p >> 13)) >> 25;
    int64_t var2_p = (((int64_t)calib->dig_P8) * p) >> 19;
    p = ((p + var1_p + var2_p) >> 8) + (((int64_t)calib->dig_P7) << 4);
    return (uint32_t)(p >> 8); // Повертає тиск у Паскалях
}
