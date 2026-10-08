#include <stdint.h>
#include <stdbool.h>

// Оптимізований табличний метод (LUT) з кусочно-лінійною інтерполяцією
typedef struct {
    float r_ohm;
    float temp_c;
} rtd_lut_entry_t;

// Таблиця вузлів від -200 °C до +100 °C з кроком 50 °C для економії пам'яті
static const rtd_lut_entry_t rtd_lut[] = {
    {18.520f, -200.0f},
    {38.521f, -150.0f},
    {60.256f, -100.0f},
    {80.306f,  -50.0f},
    {100.000f,   0.0f},
    {119.397f,  50.0f},
    {138.506f, 100.0f}
};

#define LUT_SIZE (sizeof(rtd_lut) / sizeof(rtd_lut[0]))

float rtd_interpolate_lut(float r_meas) {
    // Граничні випадки за межами діапазону
    if (r_meas <= rtd_lut[0].r_ohm) return rtd_lut[0].temp_c;
    if (r_meas >= rtd_lut[LUT_SIZE - 1].r_ohm) return rtd_lut[LUT_SIZE - 1].temp_c;

    // Бінарний пошук інтервалу в таблиці
    uint8_t low = 0;
    uint8_t high = LUT_SIZE - 1;

    while (high - low > 1) {
        uint8_t mid = (low + high) / 2;
        if (rtd_lut[mid].r_ohm > r_meas) {
            high = mid;
        } else {
            low = mid;
        }
    }

    // Лінійна інтерполяція між вузлами low та high
    float r0 = rtd_lut[low].r_ohm;
    float r1 = rtd_lut[high].r_ohm;
    float t0 = rtd_lut[low].temp_c;
    float t1 = rtd_lut[high].temp_c;

    return t0 + (r_meas - r0) * (t1 - t0) / (r1 - r0);
}
