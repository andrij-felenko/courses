#include <Arduino.h>

struct Bmp280TempCalib {
    uint16_t dig_T1;
    int16_t  dig_T2;
    int16_t  dig_T3;

    // Плаваюча крапка (double)
    float compensateTempFloat(int32_t adc_T, int32_t &out_t_fine) const {
        double var1 = (static_cast<double>(adc_T) / 16384.0 - static_cast<double>(dig_T1) / 1024.0) *
                      static_cast<double>(dig_T2);
        double var2 = ((static_cast<double>(adc_T) / 131072.0 - static_cast<double>(dig_T1) / 8192.0) *
                       (static_cast<double>(adc_T) / 131072.0 - static_cast<double>(dig_T1) / 8192.0)) *
                      static_cast<double>(dig_T3);

        out_t_fine = static_cast<int32_t>(var1 + var2);
        return static_cast<float>((var1 + var2) / 5120.0);
    }

    // Цілочисельна математика (int32_t)
    int32_t compensateTempInt32(int32_t adc_T, int32_t &out_t_fine) const {
        int32_t var1 = ((((adc_T >> 3) - (static_cast<int32_t>(dig_T1) << 1))) * static_cast<int32_t>(dig_T2)) >> 11;
        int32_t var2 = (((((adc_T >> 4) - static_cast<int32_t>(dig_T1)) *
                          ((adc_T >> 4) - static_cast<int32_t>(dig_T1))) >> 12) *
                        static_cast<int32_t>(dig_T3)) >> 14;

        out_t_fine = var1 + var2;
        return (out_t_fine * 5 + 128) >> 8; // Повертає значення у 0.01 °C
    }
};
