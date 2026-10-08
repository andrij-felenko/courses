#include <Arduino.h>

struct BME280CalibData {
    uint16_t dig_P1;
    int16_t  dig_P2, dig_P3, dig_P4, dig_P5, dig_P6, dig_P7, dig_P8, dig_P9;
    uint8_t  dig_H1;
    int16_t  dig_H2;
    uint8_t  dig_H3;
    int16_t  dig_H4, dig_H5;
    int8_t   dig_H6;
};

class BME280Math {
public:
    static float compensatePressure(int32_t adc_P, int32_t t_fine, const BME280CalibData& cal) {
        double var1 = ((double)t_fine / 2.0) - 64000.0;
        double var2 = var1 * var1 * (double)cal.dig_P6 / 32768.0;
        var2 = var2 + var1 * (double)cal.dig_P5 * 2.0;
        var2 = (var2 / 4.0) + ((double)cal.dig_P4 * 65536.0);
        var1 = ((double)cal.dig_P3 * var1 * var1 / 524288.0 + (double)cal.dig_P2 * var1) / 524288.0;
        var1 = (1.0 + var1 / 32768.0) * (double)cal.dig_P1;

        if (var1 == 0.0) return 0.0f;

        double p = 1048576.0 - (double)adc_P;
        p = (p - (var2 / 4096.0)) * 6250.0 / var1;
        double v1 = (double)cal.dig_P9 * p * p / 2147483648.0;
        double v2 = p * (double)cal.dig_P8 / 32768.0;
        p = p + (v1 + v2 + (double)cal.dig_P7) / 16.0;

        return static_cast<float>(p);
    }

    static float compensateHumidity(int32_t adc_H, int32_t t_fine, const BME280CalibData& cal) {
        double h = (double)t_fine - 76800.0;
        h = (adc_H - ((double)cal.dig_H4 * 64.0 + (double)cal.dig_H5 / 16.0 * h)) *
            ((double)cal.dig_H2 / 65536.0 * (1.0 + (double)cal.dig_H3 / 67108864.0 * h *
            (1.0 + (double)cal.dig_H6 / 67108864.0 * h * (1.0 + (double)cal.dig_H1 / 16384.0))));
        h = h * (1.0 - (double)cal.dig_H1 * h / 524288.0);

        if (h > 100.0) h = 100.0;
        if (h < 0.0) h = 0.0;
        return static_cast<float>(h);
    }
};
