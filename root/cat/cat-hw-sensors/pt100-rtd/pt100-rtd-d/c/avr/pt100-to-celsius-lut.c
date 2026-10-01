#include <stdint.h>

// Опорні точки калібрувальної таблиці PT100 (0...100 °C з кроком 10 °C)
#define PT100_LUT_START_TEMP 0.0f
#define PT100_LUT_STEP_TEMP  10.0f
#define PT100_LUT_SIZE       11

static const float pt100_lut[PT100_LUT_SIZE] = {
    100.00f, 103.90f, 107.79f, 111.67f, 115.54f,
    119.40f, 123.24f, 127.08f, 130.90f, 134.71f, 138.51f
};

// Лінеаризація опору за допомогою таблиці пошуку LUT та відрізково-лінійної інтерполяції
float pt100_to_celsius_lut(float r_measured) {
    if (r_measured <= pt100_lut[0]) {
        return PT100_LUT_START_TEMP;
    }
    if (r_measured >= pt100_lut[PT100_LUT_SIZE - 1]) {
        return PT100_LUT_START_TEMP + (float)(PT100_LUT_SIZE - 1) * PT100_LUT_STEP_TEMP;
    }

    uint8_t i = 0;
    while (i < PT100_LUT_SIZE - 2 && pt100_lut[i + 1] <= r_measured) {
        i++;
    }

    float r_low = pt100_lut[i];
    float r_high = pt100_lut[i + 1];
    float t_low = PT100_LUT_START_TEMP + (float)i * PT100_LUT_STEP_TEMP;

    return t_low + (r_measured - r_low) * PT100_LUT_STEP_TEMP / (r_high - r_low);
}
