#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

// Структура конфігурації калібрування п'єзодавача
typedef struct {
    float alpha_baseline;  // Коефіцієнт згладжування нульової лінії
    float scale_g_per_lsb; // Коефіцієнт масштабування (g на квант АЦП)
    float threshold_g;     // Поріг виявлення удару в g
} piezo_calib_t;

typedef struct {
    float baseline;        // Поточний рівень спокою DC
    bool impact_detected;  // Прапор фіксації поштовху
} piezo_state_t;

// Обробка відліку з автонулюванням та виявленням піку
float piezo_process_sample(uint16_t raw_adc, const piezo_calib_t *calib, piezo_state_t *state) {
    // 1. Адаптивне оновлення нульової лінії
    state->baseline = (calib->alpha_baseline * (float)raw_adc) + ((1.0f - calib->alpha_baseline) * state->baseline);

    // 2. Віднімання зміщення DC та обчислення амплітуди
    float signal_diff = (float)raw_adc - state->baseline;
    if (signal_diff < 0.0f) {
        signal_diff = -signal_diff;
    }

    // 3. Переведення відхилення у прискорення (g)
    float accel_g = signal_diff * calib->scale_g_per_lsb;

    // 4. Порівняння з порогом спрацьовування
    state->impact_detected = (accel_g >= calib->threshold_g);

    return accel_g;
}
