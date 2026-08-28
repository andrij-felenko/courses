#define _GNU_SOURCE
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <time.h>
#include <unistd.h>
#include <errno.h>

typedef bool (*PredicateFunc)(void* context);

/* Надійне очікування настання асинхронної події */
bool wait_until(PredicateFunc predicate, void* context, uint32_t timeout_ms, uint32_t poll_interval_ms) {
    struct timespec start_ts, current_ts;
    clock_gettime(CLOCK_MONOTONIC, &start_ts);

    uint64_t start_ms = (uint64_t)start_ts.tv_sec * 1000 + start_ts.tv_nsec / 1000000;

    while (true) {
        if (predicate(context)) {
            return true; /* Умова виконана успішно */
        }

        clock_gettime(CLOCK_MONOTONIC, &current_ts);
        uint64_t current_ms = (uint64_t)current_ts.tv_sec * 1000 + current_ts.tv_nsec / 1000000;

        if (current_ms - start_ms >= timeout_ms) {
            return false; /* Вичерпано ліміт часу */
        }

        usleep(poll_interval_ms * 1000);
    }
}
