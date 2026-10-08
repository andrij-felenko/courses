// Алгоритм двоточкового калібрування та EMA-фільтрації потенціометра на C (ESP-IDF / Generic C)
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    float adc_min;     // Код АЦП для мінімального кута
    float adc_max;     // Код АЦП для максимального кута
    float angle_min;   // Мінімальний фізичний кут (градуси або радіани)
    float angle_max;   // Максимальний фізичний кут (градуси або радіани)
    float scale;       // Обчислений коефіцієнт масштабу a
    float offset;      // Обчислений кутовий зсув b
} calibration_params_t;

typedef struct {
    float alpha;       // Коефіцієнт згладжування EMA (0 < alpha <= 1)
    float filtered_val;// Поточне відфільтроване значення
    bool is_initialized;// Прапор первинної ініціалізації
} ema_filter_t;

// Розрахунок коефіцієнтів двоточкового калібрування
void calibration_init(calibration_params_t *cal, float adc1, float angle1, float adc2, float angle2) {
    cal->adc_min = adc1;
    cal->adc_max = adc2;
    cal->angle_min = angle1;
    cal->angle_max = angle2;
    
    if (adc2 != adc1) {
        cal->scale = (angle2 - angle1) / (adc2 - adc1);
        cal->offset = angle1 - cal->scale * adc1;
    } else {
        cal->scale = 1.0f;
        cal->offset = 0.0f;
    }
}

// Перетворення сирого коду АЦП у фізичний кут
float calibration_apply(const calibration_params_t *cal, float raw_adc) {
    return cal->scale * raw_adc + cal->offset;
}

// Ініціалізація експоненційного фільтра
void ema_filter_init(ema_filter_t *filter, float alpha) {
    filter->alpha = alpha;
    filter->filtered_val = 0.0f;
    filter->is_initialized = false;
}

// Обробка нового відліку фільтром EMA
float ema_filter_update(ema_filter_t *filter, float input_val) {
    if (!filter->is_initialized) {
        filter->filtered_val = input_val;
        filter->is_initialized = true;
    } else {
        filter->filtered_val = filter->alpha * input_val + (1.0f - filter->alpha) * filter->filtered_val;
    }
    return filter->filtered_val;
}
