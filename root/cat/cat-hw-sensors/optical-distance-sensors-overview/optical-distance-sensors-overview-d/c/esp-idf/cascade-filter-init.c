#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

#define WINDOW_SIZE 5

typedef struct {
    uint16_t buffer[WINDOW_SIZE];
    uint8_t index;
    uint8_t count;
    float alpha;
    float ema_state;
    int is_initialized;
} cascade_filter_t;

void cascade_filter_init(cascade_filter_t *filter, float alpha) {
    filter->index = 0;
    filter->count = 0;
    filter->alpha = alpha;
    filter->ema_state = 0.0f;
    filter->is_initialized = 0;
}

static int compare_uint16(const void *a, const void *b) {
    uint16_t val1 = *(const uint16_t *)a;
    uint16_t val2 = *(const uint16_t *)b;
    if (val1 < val2) return -1;
    if (val1 > val2) return 1;
    return 0;
}

float cascade_filter_update(cascade_filter_t *filter, uint16_t new_sample) {
    filter->buffer[filter->index] = new_sample;
    filter->index = (filter->index + 1) % WINDOW_SIZE;
    if (filter->count < WINDOW_SIZE) {
        filter->count++;
    }

    uint16_t temp[WINDOW_SIZE];
    for (uint8_t i = 0; i < filter->count; i++) {
        temp[i] = filter->buffer[i];
    }

    qsort(temp, filter->count, sizeof(uint16_t), compare_uint16);

    uint16_t median_val = temp[filter->count / 2];

    if (!filter->is_initialized) {
        filter->ema_state = (float)median_val;
        filter->is_initialized = 1;
    } else {
        filter->ema_state = filter->alpha * (float)median_val + (1.0f - filter->alpha) * filter->ema_state;
    }

    return filter->ema_state;
}
