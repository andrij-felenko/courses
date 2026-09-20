#include "../include/stick_drift_filter.h"
#include <math.h>
#include <stddef.h>

bool stick_filter_init(stick_filter_t *filter, 
                      const stick_calibration_t *cal, 
                      float deadzone_inner, 
                      float deadzone_outer, 
                      float ema_alpha) 
{
    if (filter == NULL || cal == NULL) {
        return false;
    }

    if (deadzone_inner < 0.0f || deadzone_inner >= deadzone_outer || deadzone_outer > 1.0f) {
        return false;
    }

    if (ema_alpha <= 0.0f || ema_alpha > 1.0f) {
        return false;
    }

    /* Перевірка коректності калібрувальних діапазонів */
    if (cal->min_x >= cal->center_x || cal->center_x >= cal->max_x ||
        cal->min_y >= cal->center_y || cal->center_y >= cal->max_y) {
        return false;
    }

    filter->cal = *cal;
    filter->deadzone_inner = deadzone_inner;
    filter->deadzone_outer = deadzone_outer;
    filter->ema_alpha = ema_alpha;
    filter->filtered_x = 0.0f;
    filter->filtered_y = 0.0f;
    filter->is_initialized = false;

    return true;
}

bool stick_calibrate_center(stick_calibration_t *cal, 
                             const uint16_t *raw_x_samples, 
                             const uint16_t *raw_y_samples, 
                             size_t sample_count) 
{
    if (cal == NULL || raw_x_samples == NULL || raw_y_samples == NULL || sample_count == 0) {
        return false;
    }

    uint32_t sum_x = 0;
    uint32_t sum_y = 0;

    for (size_t i = 0; i < sample_count; i++) {
        sum_x += raw_x_samples[i];
        sum_y += raw_y_samples[i];
    }

    cal->center_x = (uint16_t)(sum_x / sample_count);
    cal->center_y = (uint16_t)(sum_y / sample_count);

    return true;
}

/**
 * @brief Несиметрична нормалізація сирого відліку АЦП у діапазон [-1.0, 1.0]
 */
static float normalize_axis(uint16_t raw, uint16_t min_val, uint16_t center_val, uint16_t max_val) {
    if (raw >= center_val) {
        uint16_t range_pos = (max_val > center_val) ? (max_val - center_val) : 1;
        float norm = (float)(raw - center_val) / (float)range_pos;
        return (norm > 1.0f) ? 1.0f : norm;
    } else {
        uint16_t range_neg = (center_val > min_val) ? (center_val - min_val) : 1;
        float norm = (float)(raw - center_val) / (float)range_neg;
        return (norm < -1.0f) ? -1.0f : norm;
    }
}

void stick_filter_process(stick_filter_t *filter, 
                         uint16_t raw_x, 
                         uint16_t raw_y, 
                         stick_output_t *out) 
{
    if (filter == NULL || out == NULL) {
        return;
    }

    /* 1. Несиметрична нормалізація сирих АЦП відносно зафіксованої нейтралі */
    float norm_x = normalize_axis(raw_x, filter->cal.min_x, filter->cal.center_x, filter->cal.max_x);
    float norm_y = normalize_axis(raw_y, filter->cal.min_y, filter->cal.center_y, filter->cal.max_y);

    /* 2. Обчислення довжини радіального вектора у полярній системі координат */
    float raw_magnitude = sqrtf(norm_x * norm_x + norm_y * norm_y);

    float scaled_x = 0.0f;
    float scaled_y = 0.0f;
    float final_magnitude = 0.0f;

    /* 3. Застосування алгоритму масштабованої радіальної мертвої зони (Scaled Radial Deadzone) */
    if (raw_magnitude > filter->deadzone_inner) {
        float dir_x = (raw_magnitude > 0.0001f) ? (norm_x / raw_magnitude) : 0.0f;
        float dir_y = (raw_magnitude > 0.0001f) ? (norm_y / raw_magnitude) : 0.0f;

        /* Обрізання за зовнішнім порогом насичення */
        float clamped_mag = (raw_magnitude > filter->deadzone_outer) ? filter->deadzone_outer : raw_magnitude;

        /* Плавне лінійне масштабування від 0.0 до 1.0 без стрибка сили */
        final_magnitude = (clamped_mag - filter->deadzone_inner) / (filter->deadzone_outer - filter->deadzone_inner);
        if (final_magnitude > 1.0f) {
            final_magnitude = 1.0f;
        }

        scaled_x = dir_x * final_magnitude;
        scaled_y = dir_y * final_magnitude;
    } else {
        /* Знаходження всередині мертвої зони: повна компенсація дрейфу нуля */
        scaled_x = 0.0f;
        scaled_y = 0.0f;
        final_magnitude = 0.0f;
    }

    /* 4. Фільтрація шумів за допомогою експоненційного ковзного середнього (EMA) */
    if (!filter->is_initialized) {
        filter->filtered_x = scaled_x;
        filter->filtered_y = scaled_y;
        filter->is_initialized = true;
    } else {
        filter->filtered_x = filter->filtered_x + filter->ema_alpha * (scaled_x - filter->filtered_x);
        filter->filtered_y = filter->filtered_y + filter->ema_alpha * (scaled_y - filter->filtered_y);
    }

    out->x = filter->filtered_x;
    out->y = filter->filtered_y;
    out->magnitude = sqrtf(out->x * out->x + out->y * out->y);
}
