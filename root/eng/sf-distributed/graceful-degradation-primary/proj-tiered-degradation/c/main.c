#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <time.h>
#include <pthread.h>
#include <unistd.h>
#include <errno.h>

#define MAX_ITEMS 8
#define STATIC_TOP_COUNT 3

/* Статичні фолбек-дані для Tier-2, розміщені в сегменті read-only пам'яті */
static const char* STATIC_TOP_RECOMMENDATIONS[STATIC_TOP_COUNT] = {
    "item_default_bestseller_1",
    "item_default_bestseller_2",
    "item_default_bestseller_3"
};

typedef struct {
    uint64_t order_id;
    double price;
    bool price_is_stale;
    const char* recommendations[MAX_ITEMS];
    size_t rec_count;
    bool is_degraded;
    uint32_t degraded_mask; /* Бітова маска деградованих рівнів */
} aggregated_response_t;

/* Отримання поточного монотонного часу в мілісекундах */
static uint64_t monotonic_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)(ts.tv_sec * 1000 + ts.tv_nsec / 1000000);
}

/* Імітація виклику сервісу з контрольованою затримкою */
typedef struct {
    uint64_t delay_ms;
    bool simulate_error;
    double result_price;
    pthread_t thread;
    bool completed;
} tier1_task_t;

static void* tier1_worker(void* arg) {
    tier1_task_t* task = (tier1_task_t*)arg;
    struct timespec ts = {
        .tv_sec = task->delay_ms / 1000,
        .tv_nsec = (task->delay_ms % 1000) * 1000000
    };
    nanosleep(&ts, NULL);
    task->result_price = 499.99;
    task->completed = true;
    return NULL;
}

typedef struct {
    uint64_t delay_ms;
    pthread_t thread;
    bool completed;
    const char* items[MAX_ITEMS];
    size_t count;
} tier2_task_t;

static void* tier2_worker(void* arg) {
    tier2_task_t* task = (tier2_task_t*)arg;
    struct timespec ts = {
        .tv_sec = task->delay_ms / 1000,
        .tv_nsec = (task->delay_ms % 1000) * 1000000
    };
    nanosleep(&ts, NULL);
    task->items[0] = "ai_personalized_watch_v2";
    task->items[1] = "ai_personalized_strap_black";
    task->count = 2;
    task->completed = true;
    return NULL;
}

/* Головний конвеєр агрегації з наскрізним контролем дедлайнів */
bool execute_aggregation(uint64_t hard_deadline_ms,
                         uint64_t tier1_sim_delay_ms,
                         uint64_t tier2_sim_delay_ms,
                         aggregated_response_t* out_resp) {
    uint64_t start_time = monotonic_ms();
    memset(out_resp, 0, sizeof(*out_resp));
    out_resp->order_id = 987654321;

    /* 1. Запуск асинхронних завдань */
    tier1_task_t t1 = { .delay_ms = tier1_sim_delay_ms, .completed = false };
    tier2_task_t t2 = { .delay_ms = tier2_sim_delay_ms, .completed = false };

    pthread_create(&t1.thread, NULL, tier1_worker, &t1);
    pthread_create(&t2.thread, NULL, tier2_worker, &t2);

    /* 2. Обробка Tier-2 (Бюджет очікування: 35 мс) */
    uint64_t t2_limit = 35;
    while (monotonic_ms() - start_time < t2_limit) {
        if (t1.completed && t2.completed) break;
        struct timespec tick = { .tv_sec = 0, .tv_nsec = 1000000 }; /* 1 мс */
        nanosleep(&tick, NULL);
    }

    if (t2.completed) {
        out_resp->rec_count = t2.count;
        for (size_t i = 0; i < t2.count; ++i) {
            out_resp->recommendations[i] = t2.items[i];
        }
    } else {
        /* Проактивна деградація Tier-2: підстановка O(1) статичного масиву */
        out_resp->is_degraded = true;
        out_resp->degraded_mask |= (1 << 2);
        out_resp->rec_count = STATIC_TOP_COUNT;
        for (size_t i = 0; i < STATIC_TOP_COUNT; ++i) {
            out_resp->recommendations[i] = STATIC_TOP_RECOMMENDATIONS[i];
        }
    }

    /* 3. Обробка Tier-1 (Бюджет очікування: 70 мс) */
    uint64_t t1_limit = 70;
    while (monotonic_ms() - start_time < t1_limit) {
        if (t1.completed) break;
        struct timespec tick = { .tv_sec = 0, .tv_nsec = 1000000 };
        nanosleep(&tick, NULL);
    }

    if (t1.completed) {
        out_resp->price = t1.result_price;
        out_resp->price_is_stale = false;
    } else {
        /* Деградація Tier-1: локальний реплікований кеш */
        out_resp->is_degraded = true;
        out_resp->degraded_mask |= (1 << 1);
        out_resp->price = 450.00; /* Кешована ціна */
        out_resp->price_is_stale = true;
    }

    /* Фонове прибирання ресурсів потоків */
    pthread_join(t1.thread, NULL);
    pthread_join(t2.thread, NULL);

    /* Перевірка жорсткого дедлайну клієнта */
    uint64_t elapsed = monotonic_ms() - start_time;
    return elapsed <= hard_deadline_ms;
}
