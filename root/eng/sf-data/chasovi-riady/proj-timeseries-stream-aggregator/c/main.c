#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <float.h>
#include <math.h>
#include <string.h>

#define BUCKET_DURATION_NS 10000000000ULL /* 10 секунд у наносекундах */
#define BUFFER_CAPACITY 64                 /* 64 слоти = 640 секунд історії */

/* Статистичний агрегат одного часового бакета */
typedef struct {
    uint64_t bucket_index; /* Абсолютний номер часового інтервалу */
    uint64_t count;        /* Кількість отриманих точок */
    double sum;            /* Сума значень */
    double min;            /* Мінімальне значення */
    double max;            /* Максимальне значення */
    double mean;           /* Поточне середнє (за Велфордом) */
    double m2;             /* Сума квадратів відхилень від середнього */
    double last_value;     /* Останнє зафіксоване значення */
    bool is_valid;         /* Чи містить бакет дані */
} TimeBucket;

/* Кільцевий буфер агрегатора часового ряду */
typedef struct {
    uint32_t series_id;
    uint64_t bucket_duration_ns;
    size_t capacity;
    TimeBucket buckets[BUFFER_CAPACITY];
    double ema_value;      /* Експоненційне ковзне середнє */
    double ema_alpha;      /* Коефіцієнт згладжування */
    bool ema_initialized;
} MetricAggregator;

/* Ініціалізація агрегатора */
void aggregator_init(MetricAggregator *agg, uint32_t series_id, double ema_alpha) {
    if (!agg) return;
    agg->series_id = series_id;
    agg->bucket_duration_ns = BUCKET_DURATION_NS;
    agg->capacity = BUFFER_CAPACITY;
    agg->ema_alpha = ema_alpha;
    agg->ema_value = 0.0;
    agg->ema_initialized = false;

    for (size_t i = 0; i < agg->capacity; i++) {
        agg->buckets[i].is_valid = false;
        agg->buckets[i].bucket_index = 0;
    }
}

/* Очищення та скидання окремого бакета під новий часовий індекс */
static void bucket_reset(TimeBucket *b, uint64_t b_idx) {
    b->bucket_index = b_idx;
    b->count = 0;
    b->sum = 0.0;
    b->min = DBL_MAX;
    b->max = -DBL_MAX;
    b->mean = 0.0;
    b->m2 = 0.0;
    b->last_value = 0.0;
    b->is_valid = true;
}

/* Додавання вимірювання в бакет за алгоритмом Велфорда */
static void bucket_update(TimeBucket *b, double val) {
    b->count++;
    b->sum += val;
    if (val < b->min) b->min = val;
    if (val > b->max) b->max = val;
    b->last_value = val;

    /* Рекурентний розрахунок середнього та дисперсії Велфорда */
    double delta = val - b->mean;
    b->mean += delta / (double)b->count;
    double delta2 = val - b->mean;
    b->m2 += delta * delta2;
}

/* Обробка нового семпла телеметрії */
bool aggregator_ingest(MetricAggregator *agg, uint64_t timestamp_ns, double val) {
    if (!agg) return false;

    uint64_t b_idx = timestamp_ns / agg->bucket_duration_ns;
    size_t slot = b_idx % agg->capacity;
    TimeBucket *target = &agg->buckets[slot];

    if (!target->is_valid) {
        bucket_reset(target, b_idx);
    } else if (target->bucket_index < b_idx) {
        /* Бакет застарів — тут у реальній системі генерується Rollup на диск */
        bucket_reset(target, b_idx);
    } else if (target->bucket_index > b_idx) {
        /* Запізнілі дані (out-of-order) старші за глибину кільцевого буфера */
        return false;
    }

    bucket_update(target, val);

    /* Оновлення потокового експоненційного середнього (EMA) */
    if (!agg->ema_initialized) {
        agg->ema_value = val;
        agg->ema_initialized = true;
    } else {
        agg->ema_value = (agg->ema_alpha * val) + ((1.0 - agg->ema_alpha) * agg->ema_value);
    }

    return true;
}

/* Отримання зведеного статистичного звіту по останньому заповненому бакету */
bool aggregator_get_latest_summary(const MetricAggregator *agg, double *out_mean,
                                   double *out_stddev, double *out_min, double *out_max) {
    if (!agg || !out_mean || !out_stddev || !out_min || !out_max) return false;

    for (size_t i = 0; i < agg->capacity; i++) {
        if (agg->buckets[i].is_valid && agg->buckets[i].count > 0) {
            const TimeBucket *b = &agg->buckets[i];
            *out_mean = b->mean;
            *out_min = b->min;
            *out_max = b->max;
            *out_stddev = (b->count > 1) ? sqrt(b->m2 / (double)(b->count - 1)) : 0.0;
            return true;
        }
    }
    return false;
}
