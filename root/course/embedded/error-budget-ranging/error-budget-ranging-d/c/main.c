#include <math.h>

typedef struct {
    float distance_mm;   // оцінка відстані
    float sigma_mm;      // випадкова невизначеність (1σ)
    float bias_mm;       // межа залишкової систематики
} Range;

// Швидкість звуку від температури: v = 331.3 + 0.606*T  (м/с, T у °C)
static float speed_of_sound(float temp_c) {
    return 331.3f + 0.606f * temp_c;
}

// t_us — виміряний повний час туди-й-назад, мкс; temp_c — температура повітря
Range range_from_tof(uint32_t t_us, float temp_c) {
    Range r;
    float v = speed_of_sound(temp_c);          // м/с — компенсуємо систематику
    float t = t_us * 1e-6f;                     // с
    r.distance_mm = v * t / 2.0f * 1000.0f;     // d = v*t/2, у мм

    // Випадкові внески (мм): таймер, джитер засічки, ціль — у квадратурі
    float s_timer  = 1.0f;
    float s_jitter = 3.0f;
    float s_target = 6.0f;
    r.sigma_mm = sqrtf(s_timer*s_timer + s_jitter*s_jitter + s_target*s_target);

    // Залишкова систематика (мм): неточність термометра + залишок калібрування нуля.
    // Температурний внесок масштабується з відстанню (це % від d).
    float temp_err_pct = 0.9f / 100.0f;         // ±0.9 % від неточності T
    float s_temp = r.distance_mm * temp_err_pct;
    float s_zero = 4.0f;
    r.bias_mm = s_temp + s_zero;                // систематику складаємо лінійно
    return r;
}
