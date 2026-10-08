#include <stdint.h>

// Цілочисельна компенсація тиску BMP280/BME280 (64-бітний формат Bosch Sensortec)
// Повертає тиск у форматі Q24.8 (256 = 1 Pa)
uint32_t bme280_compensate_pressure_int64(int32_t adc_P, int32_t t_fine, const bme280_calib_data_t *cal) {
    int64_t var1 = ((int64_t)t_fine) - 128000;
    int64_t var2 = var1 * var1 * (int64_t)cal->dig_P6;
    var2 = var2 + ((var1 * (int64_t)cal->dig_P5) << 17);
    var2 = var2 + (((int64_t)cal->dig_P4) << 35);
    var1 = ((var1 * var1 * (int64_t)cal->dig_P3) >> 8) + ((var1 * (int64_t)cal->dig_P2) << 12);
    var1 = (((((int64_t)1) << 47) + var1)) * ((int64_t)cal->dig_P1) >> 33;

    if (var1 == 0) {
        return 0; // Запобігання діленню на нуль
    }

    int64_t p = 1048576 - adc_P;
    p = (((p << 31) - var2) * 3125) / var1;
    int64_t p_var1 = (((int64_t)cal->dig_P9) * (p >> 13) * (p >> 13)) >> 25;
    int64_t p_var2 = (((int64_t)cal->dig_P8) * p) >> 19;

    p = ((p + p_var1 + p_var2) >> 8) + (((int64_t)cal->dig_P7) << 4);
    return (uint32_t)p; // Значення Q24.8 (розділити на 256.0 для Pa)
}

// Цілочисельна компенсація відносної вологості BME280 (32-бітний формат)
// Повертає вологість у форматі Q22.10 (1024 = 1 %RH)
uint32_t bme280_compensate_humidity_int32(int32_t adc_H, int32_t t_fine, const bme280_calib_data_t *cal) {
    int32_t v_x1_u32r = (t_fine - ((int32_t)76800));

    v_x1_u32r = (((((adc_H << 14) - (((int32_t)cal->dig_H4) << 20) - 
                   (((int32_t)cal->dig_H5) * v_x1_u32r)) + ((int32_t)16384)) >> 15) * 
                 (((((((v_x1_u32r * ((int32_t)cal->dig_H6)) >> 10) * 
                    (((v_x1_u32r * ((int32_t)cal->dig_H3)) >> 11) + ((int32_t)32768))) >> 10) + 
                   ((int32_t)2097152)) * ((int32_t)cal->dig_H2) + 8192) >> 14));

    v_x1_u32r = (v_x1_u32r - (((((v_x1_u32r >> 15) * (v_x1_u32r >> 15)) >> 7) * 
                               ((int32_t)cal->dig_H1)) >> 4));

    if (v_x1_u32r < 0) v_x1_u32r = 0;
    if (v_x1_u32r > 419430400) v_x1_u32r = 419430400; // 100% RH у Q22.10

    return (uint32_t)(v_x1_u32r >> 12); // Q22.10 (розділити на 1024.0 для %RH)
}
