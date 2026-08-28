/* ============================================================================
 * Метричний рушій на чистому C (C11 stdatomic)
 * Підтримує атомарні лічильники, покажчики, кумулятивні гістограми
 * та серіалізацію у формат OpenMetrics.
 * ============================================================================ */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdatomic.h>
#include <pthread.h>
#include <time.h>

#define MAX_LABEL_LEN     64
#define MAX_SERIES_NAME   64
#define MAX_HIST_BUCKETS  12
#define MAX_METRIC_SERIES 256
#define CACHE_LINE_SIZE   64

/* Типи підтримуваних метрик */
typedef enum {
    METRIC_TYPE_COUNTER,
    METRIC_TYPE_GAUGE,
    METRIC_TYPE_HISTOGRAM
} metric_type_t;

/* Структура кумулятивної гістограми з вирівнюванням */
typedef struct {
    size_t num_buckets;
    double boundaries[MAX_HIST_BUCKETS];                  /* Верхні межі кошиків (le) */
    atomic_uint_fast64_t bucket_counts[MAX_HIST_BUCKETS]; /* Кількість спостережень <= le */
    atomic_uint_fast64_t count;                           /* Загальна кількість (count) */
    _Atomic double sum;                                   /* Загальна сума значень (sum) */
} histogram_data_t;

/* Окремий часовий ряд метрики */
typedef struct {
    char name[MAX_SERIES_NAME];
    char labels[MAX_LABEL_LEN];                           /* Формат: method="GET",status="200" */
    metric_type_t type;
    union {
        atomic_uint_fast64_t counter_val;
        _Atomic double gauge_val;
        histogram_data_t hist;
    };
    bool in_use;
} metric_series_t;

/* Глобальний реєстр із захистом кардинальності */
typedef struct {
    metric_series_t series[MAX_METRIC_SERIES];
    size_t count;
    atomic_uint_fast64_t overflow_count;                 /* Лічильник відкинутих рядів */
    pthread_rwlock_t rwlock;
} metric_registry_t;

static metric_registry_t G_REGISTRY;

void registry_init(void) {
    memset(&G_REGISTRY, 0, sizeof(G_REGISTRY));
    pthread_rwlock_init(&G_REGISTRY.rwlock, NULL);
}

/* Атомарне додавання дійсного числа до _Atomic double через CAS */
static void atomic_double_add(_Atomic double *target, double val) {
    double old_val = atomic_load_explicit(target, memory_order_relaxed);
    double new_val;
    do {
        new_val = old_val + val;
    } while (!atomic_compare_exchange_weak_explicit(target, &old_val, new_val,
                                                   memory_order_relaxed,
                                                   memory_order_relaxed));
}

/* Отримання або створення часового ряду лічильника/gauge */
metric_series_t* registry_get_or_create(const char *name, const char *labels, metric_type_t type) {
    /* 1. Швидкий шлях: оптимістичний пошук під спільним read-lock */
    pthread_rwlock_rdlock(&G_REGISTRY.rwlock);
    for (size_t i = 0; i < G_REGISTRY.count; ++i) {
        if (G_REGISTRY.series[i].in_use &&
            strcmp(G_REGISTRY.series[i].name, name) == 0 &&
            strcmp(G_REGISTRY.series[i].labels, labels) == 0) {
            pthread_rwlock_unlock(&G_REGISTRY.rwlock);
            return &G_REGISTRY.series[i];
        }
    }
    pthread_rwlock_unlock(&G_REGISTRY.rwlock);

    /* 2. Повільний шлях: створення під write-lock із захистом від переповнення */
    pthread_rwlock_wrlock(&G_REGISTRY.rwlock);
    for (size_t i = 0; i < G_REGISTRY.count; ++i) {
        if (G_REGISTRY.series[i].in_use &&
            strcmp(G_REGISTRY.series[i].name, name) == 0 &&
            strcmp(G_REGISTRY.series[i].labels, labels) == 0) {
            pthread_rwlock_unlock(&G_REGISTRY.rwlock);
            return &G_REGISTRY.series[i];
        }
    }

    if (G_REGISTRY.count >= MAX_METRIC_SERIES) {
        /* Захист від вибуху кардинальності! */
        atomic_fetch_add_explicit(&G_REGISTRY.overflow_count, 1, memory_order_relaxed);
        pthread_rwlock_unlock(&G_REGISTRY.rwlock);
        return NULL;
    }

    metric_series_t *s = &G_REGISTRY.series[G_REGISTRY.count++];
    strncpy(s->name, name, MAX_SERIES_NAME - 1);
    strncpy(s->labels, labels, MAX_LABEL_LEN - 1);
    s->type = type;
    s->in_use = true;

    if (type == METRIC_TYPE_COUNTER) {
        atomic_init(&s->counter_val, 0);
    } else if (type == METRIC_TYPE_GAUGE) {
        atomic_init(&s->gauge_val, 0.0);
    }

    pthread_rwlock_unlock(&G_REGISTRY.rwlock);
    return s;
}

/* Ініціалізація гістограми з користувацькими межами */
metric_series_t* registry_register_histogram(const char *name, const char *labels,
                                            const double *buckets, size_t num_buckets) {
    pthread_rwlock_wrlock(&G_REGISTRY.rwlock);
    if (G_REGISTRY.count >= MAX_METRIC_SERIES || num_buckets > MAX_HIST_BUCKETS) {
        atomic_fetch_add_explicit(&G_REGISTRY.overflow_count, 1, memory_order_relaxed);
        pthread_rwlock_unlock(&G_REGISTRY.rwlock);
        return NULL;
    }

    metric_series_t *s = &G_REGISTRY.series[G_REGISTRY.count++];
    strncpy(s->name, name, MAX_SERIES_NAME - 1);
    strncpy(s->labels, labels, MAX_LABEL_LEN - 1);
    s->type = METRIC_TYPE_HISTOGRAM;
    s->in_use = true;

    s->hist.num_buckets = num_buckets;
    for (size_t i = 0; i < num_buckets; ++i) {
        s->hist.boundaries[i] = buckets[i];
        atomic_init(&s->hist.bucket_counts[i], 0);
    }
    atomic_init(&s->hist.count, 0);
    atomic_init(&s->hist.sum, 0.0);

    pthread_rwlock_unlock(&G_REGISTRY.rwlock);
    return s;
}

/* Операції над лічильниками */
void counter_inc(metric_series_t *s, uint64_t delta) {
    if (s && s->type == METRIC_TYPE_COUNTER) {
        atomic_fetch_add_explicit(&s->counter_val, delta, memory_order_relaxed);
    }
}

/* Операції над покажчиками */
void gauge_set(metric_series_t *s, double val) {
    if (s && s->type == METRIC_TYPE_GAUGE) {
        atomic_store_explicit(&s->gauge_val, val, memory_order_relaxed);
    }
}

/* Фіксація виміру в гістограмі */
void histogram_observe(metric_series_t *s, double val) {
    if (!s || s->type != METRIC_TYPE_HISTOGRAM) return;

    for (size_t i = 0; i < s->hist.num_buckets; ++i) {
        if (val <= s->hist.boundaries[i]) {
            atomic_fetch_add_explicit(&s->hist.bucket_counts[i], 1, memory_order_relaxed);
        }
    }
    atomic_fetch_add_explicit(&s->hist.count, 1, memory_order_relaxed);
    atomic_double_add(&s->hist.sum, val);
}

/* Рендеринг усіх метрик у формат OpenMetrics */
size_t registry_render_openmetrics(char *buffer, size_t max_len) {
    pthread_rwlock_rdlock(&G_REGISTRY.rwlock);
    size_t offset = 0;

    for (size_t i = 0; i < G_REGISTRY.count; ++i) {
        metric_series_t *s = &G_REGISTRY.series[i];
        if (!s->in_use) continue;

        if (s->type == METRIC_TYPE_COUNTER) {
            uint64_t val = atomic_load_explicit(&s->counter_val, memory_order_relaxed);
            offset += snprintf(buffer + offset, max_len - offset,
                               "# TYPE %s counter\n%s{%s} %llu\n",
                               s->name, s->name, s->labels, (unsigned long long)val);
        } else if (s->type == METRIC_TYPE_GAUGE) {
            double val = atomic_load_explicit(&s->gauge_val, memory_order_relaxed);
            offset += snprintf(buffer + offset, max_len - offset,
                               "# TYPE %s gauge\n%s{%s} %.6f\n",
                               s->name, s->name, s->labels, val);
        } else if (s->type == METRIC_TYPE_HISTOGRAM) {
            offset += snprintf(buffer + offset, max_len - offset,
                               "# TYPE %s histogram\n", s->name);
            for (size_t b = 0; b < s->hist.num_buckets; ++b) {
                uint64_t b_cnt = atomic_load_explicit(&s->hist.bucket_counts[b], memory_order_relaxed);
                offset += snprintf(buffer + offset, max_len - offset,
                                   "%s_bucket{%s,le=\"%.4f\"} %llu\n",
                                   s->name, s->labels, s->hist.boundaries[b], (unsigned long long)b_cnt);
            }
            uint64_t total_cnt = atomic_load_explicit(&s->hist.count, memory_order_relaxed);
            double total_sum = atomic_load_explicit(&s->hist.sum, memory_order_relaxed);
            offset += snprintf(buffer + offset, max_len - offset,
                               "%s_bucket{%s,le=\"+Inf\"} %llu\n"
                               "%s_sum{%s} %.6f\n"
                               "%s_count{%s} %llu\n",
                               s->name, s->labels, (unsigned long long)total_cnt,
                               s->name, s->labels, total_sum,
                               s->name, s->labels, (unsigned long long)total_cnt);
        }
    }

    uint64_t overflows = atomic_load_explicit(&G_REGISTRY.overflow_count, memory_order_relaxed);
    offset += snprintf(buffer + offset, max_len - offset,
                       "# TYPE metrics_overflow_total counter\n"
                       "metrics_overflow_total %llu\n"
                       "# EOF\n", (unsigned long long)overflows);

    pthread_rwlock_unlock(&G_REGISTRY.rwlock);
    return offset;
}
