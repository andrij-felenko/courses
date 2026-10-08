// Каскадна фільтрація рівня та розрахунок об'єму (C / ESP-IDF)
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define MEDIAN_WINDOW_SIZE 5

typedef struct {
    float buffer[MEDIAN_WINDOW_SIZE];
    size_t index;
    size_t count;
    float ema_state;
    float alpha;
    bool initialized;
} level_filter_t;

void level_filter_init(level_filter_t *filter, float alpha) {
    filter->index = 0;
    filter->count = 0;
    filter->ema_state = 0.0f;
    filter->alpha = alpha;
    filter->initialized = false;
}

// Функція порівняння для сортування медіанного вікна
static int compare_floats(const void *a, const void *b) {
    float fa = *(const float *)a;
    float fb = *(const float *)b;
    return (fa > fb) - (fa < fb);
}

float level_filter_process(level_filter_t *filter, float raw_h) {
    // 1. Додавання виміру у кільцевий буфер
    filter->buffer[filter->index] = raw_h;
    filter->index = (filter->index + 1) % MEDIAN_WINDOW_SIZE;
    if (filter->count < MEDIAN_WINDOW_SIZE) {
        filter->count++;
    }

    // 2. Медіанне фільтрування викидів
    float temp_window[MEDIAN_WINDOW_SIZE];
    for (size_t i = 0; i < filter->count; i++) {
        temp_window[i] = filter->buffer[i];
    }
    qsort(temp_window, filter->count, sizeof(float), compare_floats);
    float median_h = temp_window[filter->count / 2];

    // 3. Експоненціальне згладжування хвильових коливань
    if (!filter->initialized) {
        filter->ema_state = median_h;
        filter->initialized = true;
    } else {
        filter->ema_state = filter->alpha * median_h + (1.0f - filter->alpha) * filter->ema_state;
    }

    return filter->ema_state;
}
