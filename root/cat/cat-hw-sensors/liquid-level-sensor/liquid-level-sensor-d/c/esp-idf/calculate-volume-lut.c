#include <stdio.h>
#include <stdint.h>

typedef struct {
    float height_mm; // Висота рівня в міліметрах
    float volume_l;  // Об'єм рідини в літрах
} calibration_point_t;

// Таблиця пошуку (LUT) для калібрування резервуара
static const calibration_point_t tank_lut[] = {
    {0.0f,    0.0f},
    {100.0f,  45.0f},
    {250.0f,  180.0f},
    {500.0f,  500.0f},
    {750.0f,  820.0f},
    {900.0f,  955.0f},
    {1000.0f, 1000.0f}
};

#define LUT_SIZE (sizeof(tank_lut) / sizeof(tank_lut[0]))

float calculate_volume_lut(float current_height_mm) {
    // Крайові умови: захист від виходу за межі діапазону
    if (current_height_mm <= tank_lut[0].height_mm) {
        return tank_lut[0].volume_l;
    }
    if (current_height_mm >= tank_lut[LUT_SIZE - 1].height_mm) {
        return tank_lut[LUT_SIZE - 1].volume_l;
    }

    // Пошук інтервалу та кусково-лінійна інтерполяція
    for (size_t i = 0; i < LUT_SIZE - 1; i++) {
        if (current_height_mm >= tank_lut[i].height_mm && current_height_mm <= tank_lut[i + 1].height_mm) {
            float h0 = tank_lut[i].height_mm;
            float h1 = tank_lut[i + 1].height_mm;
            float v0 = tank_lut[i].volume_l;
            float v1 = tank_lut[i + 1].volume_l;

            return v0 + (v1 - v0) * ((current_height_mm - h0) / (h1 - h0));
        }
    }

    return 0.0f;
}
