#include <stdint.h>
#include <stdbool.h>

// Опорна таблиця опорів PT100 від -50 °C до +50 °C з кроком 10 °C
#define LUT_START_TEMP -50
#define LUT_STEP_TEMP   10
#define LUT_SIZE        11

static const float rtd_lut[LUT_SIZE] = {
    80.31f,  // -50 °C
    84.27f,  // -40 °C
    88.22f,  // -30 °C
    92.16f,  // -20 °C
    96.09f,  // -10 °C
   100.00f,  //   0 °C
   103.90f,  //  10 °C
   107.79f,  //  20 °C
   111.67f,  //  30 °C
   115.54f,  //  40 °C
   119.40f   //  50 °C
};

float rtd_lut_linear_interpolate(float r_meas) {
    if (r_meas < rtd_lut[0]) return (float)LUT_START_TEMP;
    if (r_meas >= rtd_lut[LUT_SIZE - 1]) return (float)(LUT_START_TEMP + (LUT_SIZE - 1) * LUT_STEP_TEMP);

    // Пошук відповідного інтервалу
    int i = 0;
    for (i = 0; i < LUT_SIZE - 1; i++) {
        if (r_meas >= rtd_lut[i] && r_meas < rtd_lut[i + 1]) {
            break;
        }
    }

    // Шматочно-лінійна інтерполяція
    float r_low = rtd_lut[i];
    float r_high = rtd_lut[i + 1];
    float t_low = LUT_START_TEMP + i * LUT_STEP_TEMP;

    float t_calc = t_low + (float)LUT_STEP_TEMP * (r_meas - r_low) / (r_high - r_low);
    return t_calc;
}
