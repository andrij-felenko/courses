#include <stdint.h>
#include <stdbool.h>

/* Структура конфігурації двоточкового калібратора на фіксованій комі */
typedef struct {
    int32_t raw_p1;      /* Код АЦП для першої точки (наприклад, 0 кг) */
    int32_t raw_p2;      /* Код АЦП для другої точки (наприклад, 10 кг) */
    int32_t phys_p1;     /* Фізичне значення точки 1 (у сотих долях: 0.00 кг -> 0) */
    int32_t phys_p2;     /* Фізичне значення точки 2 (у сотих долях: 10.00 кг -> 1000) */
} CalibrationConfig;

/* Експоненційний IIR-фільтр на цілочисельній арифметиці */
typedef struct {
    int32_t accumulator; /* Накопичувач високої розрядності */
    uint8_t shift_k;     /* Коефіцієнт згладжування: alpha = 1 / (2^shift_k) */
    bool initialized;
} EmaFilter;

/* Кільцевий фільтр рухомого середнього для придушення 50 Гц */
#define MA_WINDOW_SIZE 20

typedef struct {
    int32_t buffer[MA_WINDOW_SIZE];
    int32_t sum;
    uint8_t index;
    uint8_t count;
} MovingAverageFilter;

void ema_init(EmaFilter *filter, uint8_t shift_k) {
    filter->accumulator = 0;
    filter->shift_k = shift_k;
    filter->initialized = false;
}

int32_t ema_update(EmaFilter *filter, int32_t input) {
    if (!filter->initialized) {
        filter->accumulator = input << filter->shift_k;
        filter->initialized = true;
    }
    /* y[n] = y[n-1] + (x[n] - y[n-1]) / 2^K */
    filter->accumulator += input - (filter->accumulator >> filter->shift_k);
    return filter->accumulator >> filter->shift_k;
}

void ma_init(MovingAverageFilter *filter) {
    filter->sum = 0;
    filter->index = 0;
    filter->count = 0;
    for (uint8_t i = 0; i < MA_WINDOW_SIZE; ++i) {
        filter->buffer[i] = 0;
    }
}

int32_t ma_update(MovingAverageFilter *filter, int32_t input) {
    filter->sum -= filter->buffer[filter->index];
    filter->buffer[filter->index] = input;
    filter->sum += input;
    filter->index = (filter->index + 1) % MA_WINDOW_SIZE;
    if (filter->count < MA_WINDOW_SIZE) {
        filter->count++;
    }
    return filter->sum / filter->count;
}

/* Обчислення фізичної величини за двома точками калібрування */
int32_t calibrate_raw_to_phys(const CalibrationConfig *cfg, int32_t raw_adc) {
    int32_t raw_delta = cfg->raw_p2 - cfg->raw_p1;
    if (raw_delta == 0) {
        return cfg->phys_p1; /* Захист від ділення на нуль */
    }
    int64_t scaled = (int64_t)(raw_adc - cfg->raw_p1) * (cfg->phys_p2 - cfg->phys_p1);
    return cfg->phys_p1 + (int32_t)(scaled / raw_delta);
}
