/* ============================================================================
 * Інструментація бізнес-операції на C (C11)
 * ============================================================================ */
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <stdatomic.h>

/* Дескриптори метрик сервісу */
typedef struct {
    atomic_uint_fast64_t requests_total;
    atomic_uint_fast64_t errors_total;
    _Atomic double active_workers;
} service_metrics_t;

static service_metrics_t G_METRICS = {0, 0, 0.0};

/* Обробник бізнес-транзакції з фіксацією RED-метрик */
bool process_payment_transaction(uint64_t order_id, double amount) {
    struct timespec start_time, end_time;
    clock_gettime(CLOCK_MONOTONIC, &start_time);

    /* Фіксація збільшення активних обробників */
    atomic_fetch_add_explicit(&G_METRICS.requests_total, 1, memory_order_relaxed);

    bool success = true;
    if (amount <= 0.0) {
        /* Фіксація бізнес-помилки */
        atomic_fetch_add_explicit(&G_METRICS.errors_total, 1, memory_order_relaxed);
        success = false;
    } else {
        /* Імітація обробки платежу */
        success = (order_id % 7 != 0);
        if (!success) {
            atomic_fetch_add_explicit(&G_METRICS.errors_total, 1, memory_order_relaxed);
        }
    }

    clock_gettime(CLOCK_MONOTONIC, &end_time);
    double elapsed_sec = (end_time.tv_sec - start_time.tv_sec) +
                         (end_time.tv_nsec - start_time.tv_nsec) / 1e9;

    (void)elapsed_sec; /* У повній версії записується в гістограму затримок */
    return success;
}
