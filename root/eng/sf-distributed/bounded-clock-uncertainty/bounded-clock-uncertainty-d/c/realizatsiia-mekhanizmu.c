#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <unistd.h>
#include <inttypes.h>

typedef struct {
    int64_t earliest_us;
    int64_t latest_us;
} tt_interval_t;

/* Емуляція стану підсистеми часу */
typedef struct {
    int64_t base_eps_us;    /* Базова похибка еталону (мкс) */
    double drift_rate_ppm;  /* Дрейф кварцу (ppm) */
    struct timespec sync_tp;/* Час останнього скидання */
} clock_source_t;

static int64_t get_monotonic_us(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (int64_t)ts.tv_sec * 1000000LL + (int64_t)ts.tv_nsec / 1000LL;
}

tt_interval_t get_truetime_now(const clock_source_t *clk) {
    int64_t now_us = get_monotonic_us();
    int64_t sync_us = (int64_t)clk->sync_tp.tv_sec * 1000000LL + (int64_t)clk->sync_tp.tv_nsec / 1000LL;
    int64_t elapsed_us = now_us - sync_us;
    if (elapsed_us < 0) elapsed_us = 0;

    /* ε(t) = ε₀ + ρ·Δt */
    int64_t drift_us = (int64_t)((double)elapsed_us * (clk->drift_rate_ppm / 1000000.0));
    int64_t total_eps = clk->base_eps_us + drift_us;

    tt_interval_t res;
    res.earliest_us = now_us - total_eps;
    res.latest_us = now_us + total_eps;
    return res;
}

/* Бар'єр фіксації Commit Wait */
void execute_commit_wait(const clock_source_t *clk, int64_t commit_ts) {
    while (true) {
        tt_interval_t cur = get_truetime_now(clk);
        if (cur.earliest_us > commit_ts) {
            break; /* Інваріант виконано: commit_ts гарантовано в минулому */
        }
        int64_t wait_us = commit_ts - cur.earliest_us + 50;
        if (wait_us > 0) {
            struct timespec req = {
                .tv_sec = (time_t)(wait_us / 1000000LL),
                .tv_nsec = (long)((wait_us % 1000000LL) * 1000LL)
            };
            nanosleep(&req, NULL);
        }
    }
}

int main(void) {
    clock_source_t clk = {
        .base_eps_us = 1000, /* ε₀ = 1 мс */
        .drift_rate_ppm = 200.0
    };
    clock_gettime(CLOCK_MONOTONIC, &clk.sync_tp);

    printf("Ініціалізація транзакції...\n");
    tt_interval_t start_int = get_truetime_now(&clk);
    int64_t commit_ts = start_int.latest_us; /* s = latest */

    printf("Призначено мітку s = %" PRId64 " мкс (інтервал: [%" PRId64 ", %" PRId64 "])\n",
           commit_ts, start_int.earliest_us, start_int.latest_us);

    printf("Очікування Commit Wait...\n");
    execute_commit_wait(&clk, commit_ts);

    tt_interval_t end_int = get_truetime_now(&clk);
    printf("Транзакцію успішно зафіксовано. Поточний earliest = %" PRId64 " мкс (> s)\n",
           end_int.earliest_us);
    return 0;
}
