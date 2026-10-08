#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint16_t dig_P1;
    int16_t  dig_P2;
    int16_t  dig_P3;
    int16_t  dig_P4;
    int16_t  dig_P5;
    int16_t  dig_P6;
    int16_t  dig_P7;
    int16_t  dig_P8;
    int16_t  dig_P9;
    uint8_t  dig_H1;
    int16_t  dig_H2;
    uint8_t  dig_H3;
    int16_t  dig_H4;
    int16_t  dig_H5;
    int8_t   dig_H6;
} bme280_calib_data_t;

float bme280_compensate_pressure_float(int32_t adc_P, int32_t t_fine, const bme280_calib_data_t *cal) {
    float var1 = ((float)t_fine / 2.0f) - 64000.0f;
    float var2 = var1 * var1 * (float)cal->dig_P6 / 32768.0f;
    var2 = var2 + var1 * (float)cal->dig_P5 * 2.0f;
    var2 = (var2 / 4.0f) + ((float)cal->dig_P4 * 65536.0f);
    var1 = ((float)cal->dig_P3 * var1 * var1 / 524288.0f + (float)cal->dig_P2 * var1) / 524288.0f;
    var1 = (1.0f + var1 / 32768.0f) * (float)cal->dig_P1;

    if (var1 == 0.0f) {
        return 0.0f; // Запобігання діленню на нуль
    }

    float p = 1048576.0f - (float)adc_P;
    p = (p - (var2 / 4096.0f)) * 6250.0f / var1;
    var1 = (float)cal->dig_P9 * p * p / 2147483648.0f;
    var2 = p * (float)cal->dig_P8 / 32768.0f;
    p = p + (var1 + var2 + (float)cal->dig_P7) / 16.0f;

    return p; // Паскалі (Pa)
}

float bme280_compensate_humidity_float(int32_t adc_H, int32_t t_fine, const bme280_calib_data_t *cal) {
    float var_H = ((float)t_fine) - 76800.0f;
    var_H = (adc_H - (((float)cal->dig_H4) * 64.0f + ((float)cal->dig_H5) / 16.0f * var_H)) *
            (((float)cal->dig_H2) / 65536.0f * (1.0f + ((float)cal->dig_H3) / 67108864.0f * var_H *
            (1.0f + ((float)cal->dig_H6) / 67108864.0f * var_H * (1.0f + ((float)cal->dig_H1) / 16384.0f))));
    var_H = var_H * (1.0f - ((float)cal->dig_H1) * var_H / 524288.0f);

    if (var_H > 100.0f) {
        var_H = 100.0f;
    } else if (var_H < 0.0f) {
        var_H = 0.0f;
    }
    return var_H; // Відносна вологість (%RH)
}
