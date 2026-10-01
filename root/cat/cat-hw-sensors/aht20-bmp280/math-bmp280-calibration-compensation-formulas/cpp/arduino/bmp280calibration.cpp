#include <Arduino.h>

struct BMP280Calibration {
    uint16_t dig_T1;
    int16_t  dig_T2, dig_T3;
    uint16_t dig_P1;
    int16_t  dig_P2, dig_P3, dig_P4, dig_P5, dig_P6, dig_P7, dig_P8, dig_P9;
};

class BMP280Math {
public:
    static float calculateTemperature(int32_t adc_T, const BMP280Calibration& cal, int32_t& t_fine) {
        double var1 = (((double)adc_T) / 16384.0 - ((double)cal.dig_T1) / 1024.0) * ((double)cal.dig_T2);
        double var2 = ((((double)adc_T) / 131072.0 - ((double)cal.dig_T1) / 8192.0) *
                       (((double)adc_T) / 131072.0 - ((double)cal.dig_T1) / 8192.0)) * ((double)cal.dig_T3);
        t_fine = (int32_t)(var1 + var2);
        return (float)((var1 + var2) / 5120.0);
    }

    static float calculatePressure(int32_t adc_P, const BMP280Calibration& cal, int32_t t_fine) {
        double var1 = ((double)t_fine / 2.0) - 64000.0;
        double var2 = var1 * var1 * ((double)cal.dig_P6) / 32768.0;
        var2 = var2 + var1 * ((double)cal.dig_P5) * 2.0;
        var2 = (var2 / 4.0) + (((double)cal.dig_P4) * 65536.0);
        var1 = (((double)cal.dig_P3) * var1 * var1 / 524288.0 + ((double)cal.dig_P2) * var1) / 524288.0;
        var1 = (1.0 + var1 / 32768.0) * ((double)cal.dig_P1);

        if (var1 == 0.0) return 0.0f;

        double p = 1048576.0 - (double)adc_P;
        p = (p - (var2 / 4096.0)) * 6250.0 / var1;
        double var1_p = ((double)cal.dig_P9) * p * p / 2147483648.0;
        double var2_p = p * ((double)cal.dig_P8) / 32768.0;
        p = p + (var1_p + var2_p + ((double)cal.dig_P7)) / 16.0;
        return (float)p; // Повертає тиск у Паскалях
    }
};
