#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include <time.h>
#include <sched.h>
#include <unistd.h>

/* Оптимізаційний бар'єр для C: змушує компілятор вважати, що значення
   змінної val передано в непрозорий асемблерний блок */
static inline void do_not_optimize_val(uint64_t val) {
    __asm__ volatile("" : : "r,m"(val) : "memory");
}

/* Читання монотонного фізичного таймера в наносекундах */
static inline uint64_t get_time_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC_RAW, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

/* Прив'язка поточного потоку до конкретного процесорного ядра */
static bool pin_to_core(int core_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);
    return sched_setaffinity(0, sizeof(cpu_set_t), &cpuset) == 0;
}

/* Структура підсумкових статистичних результатів */
typedef struct {
    double min_ns;
    double median_ns;
    double p95_ns;
    double p99_ns;
    double iqr_ns;
} BenchmarkResult;

static int compare_doubles(const void *a, const void *b) {
    double da = *(const double *)a;
    double db = *(const double *)b;
    return (da > db) - (da < db);
}

/* Визначення перцентиля за лінійною інтерполяцією */
static double compute_percentile(const double *sorted, size_t n, double p) {
    if (n == 0) return 0.0;
    if (n == 1) return sorted[0];
    double k = p * (double)(n - 1);
    size_t i = (size_t)k;
    double f = k - (double)i;
    if (i >= n - 1) return sorted[n - 1];
    return sorted[i] + f * (sorted[i + 1] - sorted[i]);
}

/* Тип випробуваної функції: приймає цілочисельний стан або індекс */
typedef uint64_t (*BenchFunc)(uint64_t);

/* Головна функція прогону бенчмарку */
BenchmarkResult run_benchmark(BenchFunc fn, uint64_t target_batch_ns, size_t num_samples) {
    BenchmarkResult res = {0};

    /* 1. Фаза калібрування: знаходимо N ітерацій, що тривають ~ target_batch_ns (наприклад 2 мс) */
    uint64_t iters = 16;
    while (true) {
        uint64_t t0 = get_time_ns();
        for (uint64_t i = 0; i < iters; ++i) {
            uint64_t v = fn(i);
            do_not_optimize_val(v);
        }
        uint64_t dt = get_time_ns() - t0;
        if (dt >= target_batch_ns || iters >= (1ULL << 30)) {
            break;
        }
        if (dt == 0) iters *= 4;
        else iters = (iters * target_batch_ns) / dt + 1;
    }

    /* 2. Фаза прогріву (Warmup): стабілізуємо кеш і стан гілок */
    for (uint64_t i = 0; i < iters; ++i) {
        uint64_t v = fn(i);
        do_not_optimize_val(v);
    }

    /* 3. Збір вибірки незалежних зразків */
    double *samples = (double *)malloc(sizeof(double) * num_samples);
    if (!samples) return res;

    for (size_t s = 0; s < num_samples; ++s) {
        uint64_t t0 = get_time_ns();
        for (uint64_t i = 0; i < iters; ++i) {
            uint64_t v = fn(i);
            do_not_optimize_val(v);
        }
        uint64_t dt = get_time_ns() - t0;
        samples[s] = (double)dt / (double)iters;
    }

    /* 4. Сортування та розрахунок квантилів */
    qsort(samples, num_samples, sizeof(double), compare_doubles);

    res.min_ns = samples[0];
    res.median_ns = compute_percentile(samples, num_samples, 0.50);
    double q1 = compute_percentile(samples, num_samples, 0.25);
    double q3 = compute_percentile(samples, num_samples, 0.75);
    res.iqr_ns = q3 - q1;
    res.p95_ns = compute_percentile(samples, num_samples, 0.95);
    res.p99_ns = compute_percentile(samples, num_samples, 0.99);

    free(samples);
    return res;
}

/* Приклад алгоритму: 64-бітне швидке хешування (xorshift64) */
static uint64_t bench_xorshift(uint64_t state) {
    uint64_t x = state + 0x9E3779B97F4A7C15ULL;
    x ^= x >> 30;
    x *= 0xBF58476D1CE4E5B9ULL;
    x ^= x >> 27;
    x *= 0x94D049BB133111EBULL;
    x ^= x >> 31;
    return x;
}

int main(void) {
    if (pin_to_core(1)) {
        printf("Потік успішно прив'язано до CPU 1\n");
    }

    printf("Запуск мікробенчмарку xorshift64...\n");
    BenchmarkResult r = run_benchmark(bench_xorshift, 2000000ULL /* 2 мс */, 200 /* зразків */);

    printf("--- Результати ---\n");
    printf("Min:    %.3f нс / операція\n", r.min_ns);
    printf("Median: %.3f нс / операція\n", r.median_ns);
    printf("IQR:    %.3f нс\n", r.iqr_ns);
    printf("p95:    %.3f нс\n", r.p95_ns);
    printf("p99:    %.3f нс\n", r.p99_ns);

    return 0;
}
