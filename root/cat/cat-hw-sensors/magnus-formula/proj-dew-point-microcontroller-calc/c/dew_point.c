#include "dew_point.h"
#include <math.h>
#include <stdint.h>

#define MAGNUS_A 17.625f
#define MAGNUS_B 243.04f

// Метод 1: Точний розрахунок (вимагає FPU або багато тактів на софтверну плаваючу крапку)
float dew_point_math(float temp_c, float humidity_rh) {
    if (humidity_rh <= 0.0f) humidity_rh = 0.001f;
    float alpha = logf(humidity_rh / 100.0f) + (MAGNUS_A * temp_c) / (MAGNUS_B + temp_c);
    return (MAGNUS_B * alpha) / (MAGNUS_A - alpha);
}

// Метод 2: LUT (спрощена демонстрація, реальний LUT буде великим для 2D, або 1D для логарифма)
// Для прикладу використаємо грубу інтерполяцію або спрощену таблицю.
// У реальному житті LUT генерується заздалегідь скриптом.
float dew_point_lut(float temp_c, float humidity_rh) {
    // Демонстрація: лінійна апроксимація логарифма для вузького діапазону вологості (20-100%)
    // замість повноцінної великої таблиці.
    float h = humidity_rh;
    if (h < 20.0f) h = 20.0f;
    float approx_log = (h - 100.0f) * 0.015f; // Грубе наближення ln(h/100)
    
    float alpha = approx_log + (MAGNUS_A * temp_c) / (MAGNUS_B + temp_c);
    return (MAGNUS_B * alpha) / (MAGNUS_A - alpha);
}

// Метод 3: Швидка апроксимація логарифма (наприклад, через хак бітового представлення float)
static float fast_log2(float x) {
    union { float f; uint32_t i; } vx = { x };
    float y = (float)vx.i;
    y *= 1.1920928955078125e-7f; // 1 / 2^23
    return y - 126.94269504f;
}

static float fast_log(float x) {
    return fast_log2(x) * 0.69314718f; // ln(2)
}

float dew_point_fast(float temp_c, float humidity_rh) {
    if (humidity_rh <= 0.0f) humidity_rh = 0.001f;
    float alpha = fast_log(humidity_rh / 100.0f) + (MAGNUS_A * temp_c) / (MAGNUS_B + temp_c);
    return (MAGNUS_B * alpha) / (MAGNUS_A - alpha);
}
