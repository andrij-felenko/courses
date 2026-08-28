#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define WINDOW_SIZE     256
#define EXPECTED_DT_US  1000  // Очікуваний період між вибірками: 1000 мкс (1 кГц)
#define DT_TOLERANCE_US 150   // Допустимий джитер таймера ±150 мкс

typedef struct {
    int16_t  raw_samples[WINDOW_SIZE];
    uint64_t timestamps[WINDOW_SIZE];
    uint32_t head_idx;
    uint32_t count;
    uint64_t last_timestamp;
    uint32_t timing_errors;
} SensorWindowCollector;

void window_collector_init(SensorWindowCollector *w) {
    w->head_idx = 0;
    w->count = 0;
    w->last_timestamp = 0;
    w->timing_errors = 0;
}

// Додавання нової вибірки з перевіркою монотонності часу
bool window_collector_push(SensorWindowCollector *w, int16_t sample, uint64_t timestamp_us) {
    if (w->last_timestamp != 0) {
        int64_t dt = (int64_t)(timestamp_us - w->last_timestamp);
        // Перевірка на пропуск вибірки або заклинювання таймера
        if (dt < (EXPECTED_DT_US - DT_TOLERANCE_US) || dt > (EXPECTED_DT_US + DT_TOLERANCE_US)) {
            w->timing_errors++;
        }
    }
    w->last_timestamp = timestamp_us;

    w->raw_samples[w->head_idx] = sample;
    w->timestamps[w->head_idx] = timestamp_us;

    w->head_idx = (w->head_idx + 1) % WINDOW_SIZE;
    if (w->count < WINDOW_SIZE) {
        w->count++;
    }

    return (w->count == WINDOW_SIZE);
}

// Експорт лінеаризованого та нормалізованого вікна для нейромережі
bool window_collector_export(const SensorWindowCollector *w, float *out_features, float scale_factor) {
    if (w->count < WINDOW_SIZE) {
        return false;
    }

    // Вичитка циклічного буфера в хронологічному порядку
    uint32_t start_idx = w->head_idx;
    for (uint32_t i = 0; i < WINDOW_SIZE; ++i) {
        uint32_t idx = (start_idx + i) % WINDOW_SIZE;
        // Переведення в одиниці фізичної величини з нормалізацією
        out_features[i] = (float)w->raw_samples[idx] * scale_factor;
    }
    return true;
}
