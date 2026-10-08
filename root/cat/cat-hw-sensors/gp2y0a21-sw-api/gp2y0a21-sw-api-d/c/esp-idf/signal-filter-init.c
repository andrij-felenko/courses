#include <stdint.h>
#include <stdbool.h>

#define MEDIAN_WINDOW_SIZE 5

typedef struct {
    uint16_t buffer[MEDIAN_WINDOW_SIZE];
    uint8_t  index;
    bool     filled;
    uint32_t ema_state_q8; // Фіксована крапка: значення * 256
    uint16_t alpha_q8;     // Коефіцієнт alpha * 256 (наприклад, 51 для alpha = 0.2)
} signal_filter_t;

void signal_filter_init(signal_filter_t *filter, float alpha) {
    filter->index = 0;
    filter->filled = false;
    filter->ema_state_q8 = 0;
    filter->alpha_q8 = (uint16_t)(alpha * 256.0f);
}

static uint16_t get_median_5(uint16_t *src) {
    uint16_t a[MEDIAN_WINDOW_SIZE];
    for (int i = 0; i < MEDIAN_WINDOW_SIZE; i++) {
        a[i] = src[i];
    }
    // Сортування вставками для 5 елементів
    for (int i = 1; i < MEDIAN_WINDOW_SIZE; i++) {
        uint16_t key = a[i];
        int j = i - 1;
        while (j >= 0 && a[j] > key) {
            a[j + 1] = a[j];
            j--;
        }
        a[j + 1] = key;
    }
    return a[2]; // Медіанний елемент
}

uint16_t signal_filter_update(signal_filter_t *filter, uint16_t raw_adc) {
    filter->buffer[filter->index] = raw_adc;
    filter->index = (filter->index + 1) % MEDIAN_WINDOW_SIZE;
    
    if (filter->index == 0) {
        filter->filled = true;
    }

    uint16_t median_val = raw_adc;
    if (filter->filled) {
        median_val = get_median_5(filter->buffer);
    }

    // Перша ініціалізація EMA
    if (filter->ema_state_q8 == 0) {
        filter->ema_state_q8 = (uint32_t)median_val << 8;
    } else {
        // EMA: y = alpha * x + (1 - alpha) * y
        uint32_t x_q8 = (uint32_t)median_val << 8;
        filter->ema_state_q8 = (filter->alpha_q8 * x_q8 + 
                               (256 - filter->alpha_q8) * filter->ema_state_q8) >> 8;
    }

    return (uint16_t)(filter->ema_state_q8 >> 8);
}
