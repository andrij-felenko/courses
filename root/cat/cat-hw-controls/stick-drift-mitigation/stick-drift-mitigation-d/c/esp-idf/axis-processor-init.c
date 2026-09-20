#include <stdint.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    int16_t adc_min;
    int16_t adc_center;
    int16_t adc_max;
    float deadzone; // від 0.0 до 1.0
    float ema_alpha;
    float filtered_val;
} axis_processor_t;

void axis_processor_init(axis_processor_t *proc, int16_t min_v, int16_t center_v, int16_t max_v) {
    proc->adc_min = min_v;
    proc->adc_center = center_v;
    proc->adc_max = max_v;
    proc->deadzone = 0.08f; // 8% мертва зона
    proc->ema_alpha = 0.2f;
    proc->filtered_val = (float)center_v;
}

float axis_processor_step(axis_processor_t *proc, int16_t raw_adc) {
    // 1. Фільтрація EMA
    proc->filtered_val += proc->ema_alpha * ((float)raw_adc - proc->filtered_val);
    float val = proc->filtered_val;

    // 2. Двохсегментна нормалізація в діапазон [-1.0, 1.0]
    float norm = 0.0f;
    if (val < (float)proc->adc_center) {
        float span = (float)(proc->adc_center - proc->adc_min);
        if (span > 1.0f) norm = (val - (float)proc->adc_center) / span;
    } else {
        float span = (float)(proc->adc_max - proc->adc_center);
        if (span > 1.0f) norm = (val - (float)proc->adc_center) / span;
    }

    // Обмеження межами
    if (norm > 1.0f) norm = 1.0f;
    if (norm < -1.0f) norm = -1.0f;

    // 3. Застосування масштабованої мертвої зони
    float abs_norm = fabsf(norm);
    if (abs_norm < proc->deadzone) {
        return 0.0f;
    } else {
        float sign = (norm > 0.0f) ? 1.0f : -1.0f;
        float scaled = (abs_norm - proc->deadzone) / (1.0f - proc->deadzone);
        return sign * scaled;
    }
}
