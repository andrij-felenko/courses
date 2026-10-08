#include <Arduino.h>

class BME280FixedPoint {
public:
    // Повертає тиск у Паскалях як ціле число (Pa)
    static uint32_t compensatePressurePa(int32_t adc_P, int32_t t_fine, const BME280CalibData& cal) {
        int64_t v1 = ((int64_t)t_fine) - 128000;
        int64_t v2 = v1 * v1 * (int64_t)cal.dig_P6;
        v2 = v2 + ((v1 * (int64_t)cal.dig_P5) << 17);
        v2 = v2 + (((int64_t)cal.dig_P4) << 35);
        v1 = ((v1 * v1 * (int64_t)cal.dig_P3) >> 8) + ((v1 * (int64_t)cal.dig_P2) << 12);
        v1 = (((((int64_t)1) << 47) + v1)) * ((int64_t)cal.dig_P1) >> 33;

        if (v1 == 0) return 0;

        int64_t p = 1048576 - adc_P;
        p = (((p << 31) - v2) * 3125) / v1;
        int64_t p_v1 = (((int64_t)cal.dig_P9) * (p >> 13) * (p >> 13)) >> 25;
        int64_t p_v2 = (((int64_t)cal.dig_P8) * p) >> 19;

        p = ((p + p_v1 + p_v2) >> 8) + (((int64_t)cal.dig_P7) << 4);
        return static_cast<uint32_t>(p >> 8); // Переведення з Q24.8 у Паскалі
    }
};
