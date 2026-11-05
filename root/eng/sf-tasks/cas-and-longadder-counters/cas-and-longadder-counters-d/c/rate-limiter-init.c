#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>

// Суворий лімітер ресурсів на C11 атоміках
typedef struct {
    _Atomic int64_t current_tokens;
} StrictRateLimiter;

void rate_limiter_init(StrictRateLimiter* limiter, int64_t capacity) {
    atomic_init(&limiter->current_tokens, capacity);
}

bool rate_limiter_try_acquire(StrictRateLimiter* limiter) {
    int64_t current = atomic_load_explicit(&limiter->current_tokens, memory_order_relaxed);
    while (current > 0) {
        if (atomic_compare_exchange_weak_explicit(&limiter->current_tokens, &current, current - 1,
                                                 memory_order_acquire, memory_order_relaxed)) {
            return true;
        }
    }
    return false;
}

// Шардована метрика для C
typedef struct {
    _Atomic int64_t count;
    char padding[56];
} PaddedCell;

typedef struct {
    PaddedCell* cells;
    size_t mask;
} StripedMetricCounter;

void metric_counter_init(StripedMetricCounter* counter, size_t num_cells) {
    counter->mask = num_cells - 1;
    counter->cells = (PaddedCell*)calloc(num_cells, sizeof(PaddedCell));
}

void metric_counter_increment(StripedMetricCounter* counter, size_t thread_id) {
    size_t idx = thread_id & counter->mask;
    atomic_fetch_add_explicit(&counter->cells[idx].count, 1, memory_order_relaxed);
}

int64_t metric_counter_get_snapshot(const StripedMetricCounter* counter) {
    int64_t total = 0;
    for (size_t i = 0; i <= counter->mask; ++i) {
        total += atomic_load_explicit(&counter->cells[i].count, memory_order_relaxed);
    }
    return total;
}
