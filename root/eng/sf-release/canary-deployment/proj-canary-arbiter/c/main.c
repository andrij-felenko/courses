#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdatomic.h>
#include <pthread.h>
#include <unistd.h>

#define BUCKETS_COUNT 6

// ── Алгоритм FNV-1a на C ───────────────────────────────────────────────────
static inline uint32_t fnv1a_hash_c(const char* str, size_t len) {
    uint32_t hash = 2166136261u;
    for (size_t i = 0; i < len; ++i) {
        hash ^= (uint8_t)str[i];
        hash *= 16777619u;
    }
    return hash;
}

typedef enum {
    TARGET_BASELINE = 0,
    TARGET_CANARY = 1
} target_variant_t;

typedef struct {
    atomic_uint_least64_t total_requests;
    atomic_uint_least64_t failed_requests;
    atomic_uint_least64_t total_latency_us;
    atomic_uint_least64_t latency_buckets[BUCKETS_COUNT];
} request_metrics_t;

static void metrics_record(request_metrics_t* m, uint64_t latency_us, bool is_error) {
    atomic_fetch_add_explicit(&m->total_requests, 1, memory_order_relaxed);
    if (is_error) {
        atomic_fetch_add_explicit(&m->failed_requests, 1, memory_order_relaxed);
    }
    atomic_fetch_add_explicit(&m->total_latency_us, latency_us, memory_order_relaxed);

    size_t b = 0;
    if (latency_us < 10000)       b = 0;
    else if (latency_us < 25000)  b = 1;
    else if (latency_us < 50000)  b = 2;
    else if (latency_us < 100000) b = 3;
    else if (latency_us < 250000) b = 4;
    else                          b = 5;

    atomic_fetch_add_explicit(&m->latency_buckets[b], 1, memory_order_relaxed);
}

typedef struct {
    uint32_t initial_weight_pct;
    double max_error_rate_delta;
    uint32_t eval_interval_ms;
} arbiter_config_t;

typedef struct {
    arbiter_config_t config;
    atomic_uint_least32_t canary_weight_pct;
    atomic_bool is_running;
    request_metrics_t baseline_metrics;
    request_metrics_t canary_metrics;
    pthread_t thread;
} c_canary_arbiter_t;

static void emergency_rollback_c(c_canary_arbiter_t* arb, const char* reason) {
    atomic_store_explicit(&arb->canary_weight_pct, 0, memory_order_release);
    fprintf(stderr, "[ROLLBACK C] %s -> Вага канарки скинута до 0%%\n", reason);
}

static void* arbiter_thread_fn(void* arg) {
    c_canary_arbiter_t* arb = (c_canary_arbiter_t*)arg;
    while (atomic_load_explicit(&arb->is_running, memory_order_acquire)) {
        usleep(arb->config.eval_interval_ms * 1000);

        uint32_t weight = atomic_load_explicit(&arb->canary_weight_pct, memory_order_acquire);
        if (weight == 0) continue;

        uint64_t c_total = atomic_load_explicit(&arb->canary_metrics.total_requests, memory_order_relaxed);
        uint64_t b_total = atomic_load_explicit(&arb->baseline_metrics.total_requests, memory_order_relaxed);

        if (c_total < 50 || b_total < 50) continue;

        uint64_t c_err = atomic_load_explicit(&arb->canary_metrics.failed_requests, memory_order_relaxed);
        uint64_t b_err = atomic_load_explicit(&arb->baseline_metrics.failed_requests, memory_order_relaxed);

        double c_rate = (double)c_err / (double)c_total;
        double b_rate = (double)b_err / (double)b_total;

        if (c_rate > b_rate + arb->config.max_error_rate_delta) {
            char buf[256];
            snprintf(buf, sizeof(buf), "Перевищення помилок: Canary=%.2f%% vs Baseline=%.2f%%", c_rate * 100.0, b_rate * 100.0);
            emergency_rollback_c(arb, buf);
            continue;
        }

        uint64_t tail_count = atomic_load_explicit(&arb->canary_metrics.latency_buckets[5], memory_order_relaxed);
        double tail_ratio = (double)tail_count / (double)c_total;
        if (tail_ratio > 0.01) {
            char buf[256];
            snprintf(buf, sizeof(buf), "Висока затримка p99: >250мс для %.2f%% запитів", tail_ratio * 100.0);
            emergency_rollback_c(arb, buf);
        }
    }
    return NULL;
}

c_canary_arbiter_t* arbiter_create(arbiter_config_t cfg) {
    c_canary_arbiter_t* arb = (c_canary_arbiter_t*)calloc(1, sizeof(c_canary_arbiter_t));
    if (!arb) return NULL;

    arb->config = cfg;
    atomic_init(&arb->canary_weight_pct, cfg.initial_weight_pct);
    atomic_init(&arb->is_running, true);

    pthread_create(&arb->thread, NULL, arbiter_thread_fn, arb);
    return arb;
}

void arbiter_destroy(c_canary_arbiter_t* arb) {
    if (!arb) return;
    atomic_store_explicit(&arb->is_running, false, memory_order_release);
    pthread_join(arb->thread, NULL);
    free(arb);
}

target_variant_t arbiter_route(c_canary_arbiter_t* arb, const char* user_id, size_t len) {
    uint32_t weight = atomic_load_explicit(&arb->canary_weight_pct, memory_order_acquire);
    if (weight == 0) return TARGET_BASELINE;

    uint32_t bucket = fnv1a_hash_c(user_id, len) % 100;
    return (bucket < weight) ? TARGET_CANARY : TARGET_BASELINE;
}
