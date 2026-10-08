#define LM35_SMA_BUFFER_SIZE 8

// Структура фільтра SMA
typedef struct {
    float buffer[LM35_SMA_BUFFER_SIZE];
    uint8_t index;
    uint8_t count;
    float sum;
} lm35_sma_filter_t;

// Структура фільтра EMA
typedef struct {
    float alpha;            // Коефіцієнт згладжування (0.0 < alpha <= 1.0)
    float filtered_value;   // Поточний стан фільтра
    bool initialized;       // Прапорець первинної ініціалізації
} lm35_ema_filter_t;

// Ініціалізація SMA
void lm35_sma_init(lm35_sma_filter_t *f) {
    f->index = 0;
    f->count = 0;
    f->sum = 0.0f;
}

// Обробка значення фільтром SMA
float lm35_sma_update(lm35_sma_filter_t *f, float input) {
    if (f->count < LM35_SMA_BUFFER_SIZE) {
        f->buffer[f->index] = input;
        f->sum += input;
        f->count++;
    } else {
        f->sum -= f->buffer[f->index];
        f->buffer[f->index] = input;
        f->sum += input;
    }
    f->index = (f->index + 1) % LM35_SMA_BUFFER_SIZE;
    return f->sum / (float)f->count;
}

// Ініціалізація EMA
void lm35_ema_init(lm35_ema_filter_t *f, float alpha) {
    f->alpha = (alpha > 0.0f && alpha <= 1.0f) ? alpha : 0.1f;
    f->filtered_value = 0.0f;
    f->initialized = false;
}

// Обробка значення фільтром EMA
float lm35_ema_update(lm35_ema_filter_t *f, float input) {
    if (!f->initialized) {
        f->filtered_value = input;
        f->initialized = true;
    } else {
        f->filtered_value = (f->alpha * input) + ((1.0f - f->alpha) * f->filtered_value);
    }
    return f->filtered_value;
}
