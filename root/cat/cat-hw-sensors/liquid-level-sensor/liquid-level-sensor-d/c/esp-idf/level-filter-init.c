#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>

#define MEDIAN_WINDOW_SIZE 5

typedef struct {
    float raw_samples[MEDIAN_WINDOW_SIZE];
    uint8_t sample_index;
    float ema_value;
    float alpha;
    bool is_initialized;
} level_filter_t;

void level_filter_init(level_filter_t *filter, float alpha) {
    filter->sample_index = 0;
    filter->alpha = alpha;
    filter->ema_value = 0.0f;
    filter->is_initialized = false;
    for (int i = 0; i < MEDIAN_WINDOW_SIZE; i++) {
        filter->raw_samples[i] = 0.0f;
    }
}

static int compare_floats(const void *a, const void *b) {
    float fa = *(const float *)a;
    float fb = *(const float *)b;
    return (fa > fb) - (fa < fb);
}

float level_filter_update(level_filter_t *filter, float new_raw_value) {
    // Запис нового значення у кільцевий буфер
    filter->raw_samples[filter->sample_index] = new_raw_value;
    filter->sample_index = (filter->sample_index + 1) % MEDIAN_WINDOW_SIZE;

    // Копіювання масиву для сортування (медіанна фільтрація)
    float sorted_window[MEDIAN_WINDOW_SIZE];
    for (int i = 0; i < MEDIAN_WINDOW_SIZE; i++) {
        sorted_window[i] = filter->raw_samples[i];
    }
    qsort(sorted_window, MEDIAN_WINDOW_SIZE, sizeof(float), compare_floats);
    float median_val = sorted_window[MEDIAN_WINDOW_SIZE / 2];

    // Експоненційне ковзне усереднення (EMA)
    if (!filter->is_initialized) {
        filter->ema_value = median_val;
        filter->is_initialized = true;
    } else {
        filter->ema_value = filter->alpha * median_val + (1.0f - filter->alpha) * filter->ema_value;
    }

    return filter->ema_value;
}
