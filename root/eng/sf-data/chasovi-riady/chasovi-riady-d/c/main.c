#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/* Структура одного семпла часового ряду */
typedef struct {
    uint32_t series_id;  /* Ідентифікатор часового ряду */
    uint64_t timestamp;  /* Час у наносекундах */
    double value;        /* Виміряне числове значення */
} MetricSample;

/* Стан фільтра експоненційного згладжування */
typedef struct {
    double alpha;
    double current_ema;
    bool is_initialized;
} EmaFilter;

void ema_init(EmaFilter *filter, double alpha) {
    if (!filter) return;
    filter->alpha = (alpha > 0.0 && alpha <= 1.0) ? alpha : 0.2;
    filter->current_ema = 0.0;
    filter->is_initialized = false;
}

double ema_update(EmaFilter *filter, double new_value) {
    if (!filter) return 0.0;
    if (!filter->is_initialized) {
        filter->current_ema = new_value;
        filter->is_initialized = true;
    } else {
        filter->current_ema = (filter->alpha * new_value) + 
                              ((1.0 - filter->alpha) * filter->current_ema);
    }
    return filter->current_ema;
}

/* Лінійна інтерполяція значення для пропущеного часу t_target */
bool linear_interpolate(const MetricSample *p1, const MetricSample *p2, 
                        uint64_t t_target, double *out_value) {
    if (!p1 || !p2 || !out_value) return false;
    if (t_target < p1->timestamp || t_target > p2->timestamp) return false;
    if (p1->timestamp == p2->timestamp) {
        *out_value = p1->value;
        return true;
    }

    double ratio = (double)(t_target - p1->timestamp) / 
                   (double)(p2->timestamp - p1->timestamp);
    *out_value = p1->value + ratio * (p2->value - p1->value);
    return true;
}
