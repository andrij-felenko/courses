#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <pthread.h>
#include <unistd.h>
#include <inttypes.h>

/* Часовий інтервал TrueTime в мікросекундах */
typedef struct {
    int64_t earliest;
    int64_t latest;
} tt_interval_t;

/* Стан локального годинника вузла */
typedef struct {
    int64_t base_uncertainty_us; /* Базова похибка еталону (ε₀) */
    double drift_rate_ppm;       /* Максимальний дрейф генератора в ppm */
    struct timespec last_sync;   /* Момент останньої синхронізації */
    int64_t offset_bias_us;      /* Штучний зсув шкали вузла */
    pthread_mutex_t lock;
} tt_clock_node_t;

static int64_t timespec_to_us(const struct timespec *ts) {
    return (int64_t)ts->tv_sec * 1000000LL + (int64_t)ts->tv_nsec / 1000LL;
}

static void us_to_timespec(int64_t us, struct timespec *ts) {
    ts->tv_sec = (time_t)(us / 1000000LL);
    ts->tv_nsec = (long)((us % 1000000LL) * 1000LL);
}

/* Ініціалізація локального часового вузла */
void tt_node_init(tt_clock_node_t *node, int64_t base_eps_us, double drift_ppm, int64_t bias_us) {
    node->base_uncertainty_us = base_eps_us;
    node->drift_rate_ppm = drift_ppm;
    node->offset_bias_us = bias_us;
    clock_gettime(CLOCK_MONOTONIC, &node->last_sync);
    pthread_mutex_init(&node->lock, NULL);
}

void tt_node_destroy(tt_clock_node_t *node) {
    pthread_mutex_destroy(&node->lock);
}

/* Отримання поточного інтервалу TrueTime */
tt_interval_t tt_now(tt_clock_node_t *node) {
    struct timespec now_ts;
    clock_gettime(CLOCK_MONOTONIC, &now_ts);

    pthread_mutex_lock(&node->lock);
    int64_t now_us = timespec_to_us(&now_ts) + node->offset_bias_us;
    int64_t elapsed_us = timespec_to_us(&now_ts) - timespec_to_us(&node->last_sync);
    if (elapsed_us < 0) elapsed_us = 0;

    /* Динамічне зростання невизначеності: ε(t) = ε₀ + ρ·Δt */
    int64_t drift_us = (int64_t)((double)elapsed_us * (node->drift_rate_ppm / 1000000.0));
    int64_t total_eps = node->base_uncertainty_us + drift_us;
    pthread_mutex_unlock(&node->lock);

    tt_interval_t interval;
    interval.earliest = now_us - total_eps;
    interval.latest = now_us + total_eps;
    return interval;
}

/* Перевірка, чи момент t гарантовано настав у фізичному часі */
bool tt_after(tt_clock_node_t *node, int64_t t) {
    tt_interval_t cur = tt_now(node);
    return cur.earliest > t;
}

/* Перевірка, чи момент t гарантовано ще не настав */
bool tt_before(tt_clock_node_t *node, int64_t t) {
    tt_interval_t cur = tt_now(node);
    return cur.latest < t;
}

/* Бар'єр Commit Wait: блокування потоку доки earliest > s */
void tt_commit_wait(tt_clock_node_t *node, int64_t commit_ts) {
    while (!tt_after(node, commit_ts)) {
        tt_interval_t cur = tt_now(node);
        int64_t remaining_us = commit_ts - cur.earliest + 50; /* +50 мкс захисний інтервал */
        if (remaining_us > 0) {
            struct timespec req;
            us_to_timespec(remaining_us, &req);
            nanosleep(&req, NULL);
        }
    }
}

/* Демонстрація виконання розподілених транзакцій */
typedef struct {
    tt_clock_node_t *node_a;
    tt_clock_node_t *node_b;
    int64_t tx1_commit_ts;
    int64_t tx2_commit_ts;
    bool violation_detected;
} test_context_t;

void* worker_thread(void *arg) {
    test_context_t *ctx = (test_context_t*)arg;

    /* Транзакція T1 на Вузлі А */
    tt_interval_t int1 = tt_now(ctx->node_a);
    int64_t s1 = int1.latest; /* Вибір мітки коміту: s1 = latest */
    
    printf("[Tx1 Вузол A] Обрано мітку s1 = %" PRId64 " мкс (інтервал: [%" PRId64 ", %" PRId64 "])\n",
           s1, int1.earliest, int1.latest);

    /* Бар'єр очікування на Вузлі А */
    tt_commit_wait(ctx->node_a, s1);
    ctx->tx1_commit_ts = s1;
    printf("[Tx1 Вузол A] Зафіксовано після Commit Wait. Відповідь повернено клієнту.\n");

    /* Імітація зовнішньої передачі даних від клієнта 1 до клієнта 2 (5 мс) */
    usleep(5000);

    /* Транзакція T2 на Вузлі B (який має значний від'ємний зсув годинника!) */
    tt_interval_t int2 = tt_now(ctx->node_b);
    int64_t s2 = int2.latest;
    printf("[Tx2 Вузол B] Обрано мітку s2 = %" PRId64 " мкс (інтервал: [%" PRId64 ", %" PRId64 "])\n",
           s2, int2.earliest, int2.latest);

    tt_commit_wait(ctx->node_b, s2);
    ctx->tx2_commit_ts = s2;
    printf("[Tx2 Вузол B] Зафіксовано. s2 = %" PRId64 "\n", s2);

    /* Перевірка інваріанта лінеаризовності: s1 < s2 */
    if (s2 <= s1) {
        printf("ПОМИЛКА: Порушення лінеаризовності! s2 (%" PRId64 ") <= s1 (%" PRId64 ")\n", s2, s1);
        ctx->violation_detected = true;
    } else {
        printf("УСПІХ: Порядок збережено: s1 (%" PRId64 ") < s2 (%" PRId64 ") [Δ = %" PRId64 " мкс]\n",
               s1, s2, s2 - s1);
    }
    return NULL;
}

int main(void) {
    tt_clock_node_t node_a, node_b;
    /* Вузол A: похибка 2000 мкс (2 мс), випереджає еталон на +1000 мкс */
    tt_node_init(&node_a, 2000, 200.0, 1000);
    /* Вузол B: похибка 2000 мкс (2 мс), суттєво відстає: зсув -4000 мкс */
    tt_node_init(&node_b, 2000, 200.0, -4000);

    test_context_t ctx = { &node_a, &node_b, 0, 0, false };
    pthread_t th;
    pthread_create(&th, NULL, worker_thread, &ctx);
    pthread_join(th, NULL);

    tt_node_destroy(&node_a);
    tt_node_destroy(&node_b);
    return ctx.violation_detected ? 1 : 0;
}
