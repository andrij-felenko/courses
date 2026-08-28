#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <pthread.h>

typedef enum {
    GATE_ALLOW_DEPLOYMENT = 0,
    GATE_THROTTLE_RELEASES = 1,
    GATE_FREEZE_RELEASES_PAGE = 2
} GateVerdict;

typedef struct {
    uint64_t total_requests;
    uint64_t good_requests;
    uint64_t bad_requests;
} EventBucket;

typedef struct {
    double target_sli;              // Наприклад, 0.999
    uint32_t long_window_sec;       // 3600 сек (1 година)
    uint32_t short_window_sec;      // 300 сек (5 хвилин)
    double critical_burn_rate;      // 14.4
    double warning_burn_rate;       // 6.0
    uint32_t bucket_duration_sec;   // 10 сек
} SloConfig;

typedef struct {
    SloConfig config;
    EventBucket* buckets;
    size_t total_buckets;
    size_t head_index;
    size_t short_window_buckets;
    size_t long_window_buckets;
    time_t last_bucket_time;
    pthread_rwlock_t rwlock;
} SloEngine;

SloEngine* slo_engine_create(SloConfig config) {
    SloEngine* engine = (SloEngine*)malloc(sizeof(SloEngine));
    if (!engine) return NULL;

    engine->config = config;
    engine->total_buckets = (config.long_window_sec / config.bucket_duration_sec) + 1;
    engine->buckets = (EventBucket*)calloc(engine->total_buckets, sizeof(EventBucket));
    if (!engine->buckets) {
        free(engine);
        return NULL;
    }

    engine->head_index = 0;
    engine->short_window_buckets = config.short_window_sec / config.bucket_duration_sec;
    engine->long_window_buckets = config.long_window_sec / config.bucket_duration_sec;
    engine->last_bucket_time = time(NULL);
    pthread_rwlock_init(&engine->rwlock, NULL);

    return engine;
}

void slo_engine_destroy(SloEngine* engine) {
    if (!engine) return;
    pthread_rwlock_destroy(&engine->rwlock);
    free(engine->buckets);
    free(engine);
}

static void advance_buckets(SloEngine* engine, time_t now) {
    time_t elapsed = now - engine->last_bucket_time;
    if (elapsed < (time_t)engine->config.bucket_duration_sec) {
        return;
    }

    size_t steps = (size_t)(elapsed / engine->config.bucket_duration_sec);
    if (steps > engine->total_buckets) {
        steps = engine->total_buckets;
    }

    for (size_t s = 0; s < steps; ++s) {
        engine->head_index = (engine->head_index + 1) % engine->total_buckets;
        memset(&engine->buckets[engine->head_index], 0, sizeof(EventBucket));
    }

    engine->last_bucket_time = now;
}

void slo_engine_record(SloEngine* engine, bool is_good, uint64_t count) {
    if (!engine) return;
    time_t now = time(NULL);

    pthread_rwlock_wrlock(&engine->rwlock);
    advance_buckets(engine, now);

    EventBucket* cur = &engine->buckets[engine->head_index];
    cur->total_requests += count;
    if (is_good) {
        cur->good_requests += count;
    } else {
        cur->bad_requests += count;
    }
    pthread_rwlock_unlock(&engine->rwlock);
}

static double calculate_burn_rate_locked(const SloEngine* engine, size_t window_buckets) {
    uint64_t total = 0;
    uint64_t bad = 0;

    size_t count = window_buckets;
    if (count > engine->total_buckets) count = engine->total_buckets;

    for (size_t i = 0; i < count; ++i) {
        size_t idx = (engine->head_index + engine->total_buckets - i) % engine->total_buckets;
        total += engine->buckets[idx].total_requests;
        bad += engine->buckets[idx].bad_requests;
    }

    if (total == 0) return 0.0;

    double actual_error_rate = (double)bad / (double)total;
    double allowed_error_rate = 1.0 - engine->config.target_sli;
    if (allowed_error_rate <= 0.0) return 0.0;

    return actual_error_rate / allowed_error_rate;
}

GateVerdict slo_engine_evaluate(SloEngine* engine) {
    if (!engine) return GATE_ALLOW_DEPLOYMENT;

    pthread_rwlock_rdlock(&engine->rwlock);
    double short_burn = calculate_burn_rate_locked(engine, engine->short_window_buckets);
    double long_burn = calculate_burn_rate_locked(engine, engine->long_window_buckets);
    pthread_rwlock_unlock(&engine->rwlock);

    if (short_burn >= engine->config.critical_burn_rate && 
        long_burn >= engine->config.critical_burn_rate) {
        return GATE_FREEZE_RELEASES_PAGE;
    }

    if (short_burn >= engine->config.warning_burn_rate && 
        long_burn >= engine->config.warning_burn_rate) {
        return GATE_THROTTLE_RELEASES;
    }

    return GATE_ALLOW_DEPLOYMENT;
}

int main(void) {
    SloConfig config = {
        .target_sli = 0.999,
        .long_window_sec = 3600,
        .short_window_sec = 300,
        .critical_burn_rate = 14.4,
        .warning_burn_rate = 6.0,
        .bucket_duration_sec = 10
    };

    SloEngine* engine = slo_engine_create(config);
    if (!engine) {
        fprintf(stderr, "Помилка виділення пам'яті для SloEngine\n");
        return 1;
    }

    // Запис успішних подій
    for (int i = 0; i < 999; ++i) {
        slo_engine_record(engine, true, 1);
    }
    slo_engine_record(engine, false, 1);

    GateVerdict v1 = slo_engine_evaluate(engine);
    printf("Стан 1 (Стабільний потік): %s\n", 
           v1 == GATE_ALLOW_DEPLOYMENT ? "ALLOW" : "BLOCKED");

    // Імітація аварії
    for (int i = 0; i < 100; ++i) {
        slo_engine_record(engine, false, 1);
    }

    GateVerdict v2 = slo_engine_evaluate(engine);
    printf("Стан 2 (Під час аварії): %s\n", 
           v2 == GATE_FREEZE_RELEASES_PAGE ? "FREEZE_AND_PAGE" : "NORMAL");

    slo_engine_destroy(engine);
    return 0;
}
