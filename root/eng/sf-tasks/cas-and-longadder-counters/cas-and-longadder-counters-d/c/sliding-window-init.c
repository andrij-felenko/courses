#include <stdatomic.h>
#include <stdint.h>
#include <stdlib.h>
#include <time.h>
#include <stdbool.h>

typedef struct {
    _Atomic int64_t timestamp;
    _Atomic int64_t counter;
    char padding[48]; // Падінг для запобігання false sharing між кошиками
} TimeBucket;

typedef struct {
    int64_t window_size;
    TimeBucket* buckets;
} SlidingWindowCounter;

void sliding_window_init(SlidingWindowCounter* sw, int64_t window_seconds) {
    sw->window_size = window_seconds;
    sw->buckets = (TimeBucket*)calloc(window_seconds, sizeof(TimeBucket));
    for (int64_t i = 0; i < window_seconds; i++) {
        atomic_init(&sw->buckets[i].timestamp, -1);
        atomic_init(&sw->buckets[i].counter, 0);
    }
}

static int64_t get_current_sec(void) {
    return (int64_t)time(NULL);
}

void sliding_window_increment(SlidingWindowCounter* sw) {
    int64_t now_sec = get_current_sec();
    size_t index = (size_t)(now_sec % sw->window_size);
    TimeBucket* bucket = &sw->buckets[index];

    int64_t bucket_time = atomic_load_explicit(&bucket->timestamp, memory_order_relaxed);
    if (bucket_time != now_sec) {
        if (atomic_compare_exchange_strong_explicit(&bucket->timestamp, &bucket_time, now_sec,
                                                   memory_order_acq_rel, memory_order_relaxed)) {
            atomic_store_explicit(&bucket->counter, 0, memory_order_relaxed);
        }
    }
    atomic_fetch_add_explicit(&bucket->counter, 1, memory_order_relaxed);
}

int64_t sliding_window_get_sum(const SlidingWindowCounter* sw) {
    int64_t now_sec = get_current_sec();
    int64_t total_sum = 0;

    for (int64_t i = 0; i < sw->window_size; i++) {
        int64_t bucket_time = atomic_load_explicit(&sw->buckets[i].timestamp, memory_order_acquire);
        if (now_sec - bucket_time < sw->window_size && bucket_time > 0) {
            total_sum += atomic_load_explicit(&sw->buckets[i].counter, memory_order_relaxed);
        }
    }
    return total_sum;
}
