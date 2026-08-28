#include <stdint.h>
#include <stdbool.h>

#define ADC_CHANNELS_COUNT 3
#define MEDIAN_WINDOW_SIZE 3
#define EMA_ALPHA_FP_SHIFT 8  /* Фіксована кома: масштаб 256 */
#define EMA_ALPHA_FP       38 /* alpha = 38 / 256 ≈ 0.15 */

/* Структура конфігурації фільтра для одного каналу */
typedef struct {
    uint16_t history[MEDIAN_WINDOW_SIZE];
    uint8_t  history_idx;
    uint32_t ema_accumulator; /* Накопичувач з фіксованою комою Q24.8 */
    bool     initialized;
} AdcChannelFilter;

/* Стан синхронізованого драйвера */
typedef struct {
    volatile uint16_t dma_raw_buffer[ADC_CHANNELS_COUNT];
    AdcChannelFilter  filters[ADC_CHANNELS_COUNT];
    uint16_t          filtered_values[ADC_CHANNELS_COUNT];
} SynchronizedAdcDriver;

/* Швидкий пошук медіани 3 чисел без розгалужень на масивах */
static inline uint16_t median_of_three(uint16_t a, uint16_t b, uint16_t c) {
    if (a > b) {
        if (b > c) return b;
        if (a > c) return c;
        return a;
    } else {
        if (a > c) return a;
        if (b > c) return c;
        return b;
    }
}

/* Ініціалізація структур фільтрації */
void adc_driver_init(SynchronizedAdcDriver *driver) {
    for (uint32_t ch = 0; ch < ADC_CHANNELS_COUNT; ++ch) {
        driver->dma_raw_buffer[ch] = 0;
        driver->filtered_values[ch] = 0;
        driver->filters[ch].history_idx = 0;
        driver->filters[ch].ema_accumulator = 0;
        driver->filters[ch].initialized = false;
        for (uint32_t i = 0; i < MEDIAN_WINDOW_SIZE; ++i) {
            driver->filters[ch].history[i] = 0;
        }
    }
}

/* Обробка нових відліків АЦП (викликається в DMA-перериванні або циклі) */
void adc_driver_process_sample(SynchronizedAdcDriver *driver) {
    for (uint32_t ch = 0; ch < ADC_CHANNELS_COUNT; ++ch) {
        uint16_t raw_sample = driver->dma_raw_buffer[ch];
        AdcChannelFilter *f = &driver->filters[ch];

        /* Оновлення кільцевого буфера історії */
        f->history[f->history_idx] = raw_sample;
        f->history_idx = (f->history_idx + 1) % MEDIAN_WINDOW_SIZE;

        /* Каскад 1: 3-точковий медіанний фільтр */
        uint16_t median_val = median_of_three(f->history[0], f->history[1], f->history[2]);

        /* Каскад 2: Експоненційний IIR-фільтр з фіксованою комою */
        if (!f->initialized) {
            f->ema_accumulator = ((uint32_t)median_val) << EMA_ALPHA_FP_SHIFT;
            f->initialized = true;
        } else {
            /* EMA: acc = acc + alpha * (median - acc) */
            int32_t current_val_fp = ((int32_t)median_val) << EMA_ALPHA_FP_SHIFT;
            int32_t diff = current_val_fp - (int32_t)f->ema_accumulator;
            f->ema_accumulator += (diff * EMA_ALPHA_FP) >> EMA_ALPHA_FP_SHIFT;
        }

        /* Вихідне згладжене значення */
        driver->filtered_values[ch] = (uint16_t)(f->ema_accumulator >> EMA_ALPHA_FP_SHIFT);
    }
}

/* Отримання очищеного результату вимірювання каналу */
uint16_t adc_driver_get_channel_value(const SynchronizedAdcDriver *driver, uint32_t channel) {
    if (channel >= ADC_CHANNELS_COUNT) {
        return 0;
    }
    return driver->filtered_values[channel];
}
