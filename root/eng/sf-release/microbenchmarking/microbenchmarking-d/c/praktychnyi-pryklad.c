#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <time.h>
#include <sched.h>

static inline void do_not_optimize(uint64_t v) {
    __asm__ volatile("" : : "r,m"(v) : "memory");
}

static inline uint64_t get_time_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC_RAW, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

/* Метод 1: Наївний побітовий прохід */
static uint64_t popcount_naive(uint64_t x) {
    uint64_t count = 0;
    while (x) {
        count += (x & 1ULL);
        x >>= 1ULL;
    }
    return count;
}

/* Метод 2: Вбудована апаратна інструкція CPU (POPCNT) */
static uint64_t popcount_builtin(uint64_t x) {
    return (uint64_t)__builtin_popcountll(x);
}

typedef uint64_t (*PopcountFn)(uint64_t);

static double benchmark_popcount(PopcountFn fn, const uint64_t *data, size_t size, size_t iters) {
    // Фаза прогріву
    for (size_t i = 0; i < size; ++i) {
        uint64_t res = fn(data[i]);
        do_not_optimize(res);
    }

    uint64_t t0 = get_time_ns();
    for (size_t it = 0; it < iters; ++it) {
        for (size_t i = 0; i < size; ++i) {
            uint64_t res = fn(data[i]);
            do_not_optimize(res);
        }
    }
    uint64_t dt = get_time_ns() - t0;
    return (double)dt / (double)(size * iters);
}

int main(void) {
    // Фіксація потоку на ядрі 0 для усунення міграції
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(0, &cpuset);
    sched_setaffinity(0, sizeof(cpu_set_t), &cpuset);

    const size_t N = 1024;
    uint64_t test_data[N];
    for (size_t i = 0; i < N; ++i) {
        test_data[i] = ((uint64_t)rand() << 32) | (uint64_t)rand();
    }

    double t_naive = benchmark_popcount(popcount_naive, test_data, N, 10000);
    double t_builtin = benchmark_popcount(popcount_builtin, test_data, N, 10000);

    printf("popcount_naive:   %.3f нс / операція\n", t_naive);
    printf("popcount_builtin: %.3f нс / операція\n", t_builtin);
    printf("Прискорення:      %.2fx\n", t_naive / t_builtin);

    return 0;
}
