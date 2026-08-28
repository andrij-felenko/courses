#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <stdint.h>
#include <math.h>

// Структура накопичення статистичних замірів у наносекундах
typedef struct {
    uint64_t* samples;
    size_t capacity;
    size_t count;
} benchmark_stats_t;

// Ініціалізація буфера замірів з попереднім виділенням пам'яті
int benchmark_stats_init(benchmark_stats_t* stats, size_t capacity) {
    stats->samples = (uint64_t*)malloc(capacity * sizeof(uint64_t));
    if (!stats->samples) return -1;
    stats->capacity = capacity;
    stats->count = 0;
    return 0;
}

// Звільнення ресурсів
void benchmark_stats_free(benchmark_stats_t* stats) {
    if (stats->samples) {
        free(stats->samples);
        stats->samples = NULL;
    }
    stats->capacity = 0;
    stats->count = 0;
}

// Запис нового заміру у наносекундах
void benchmark_stats_add(benchmark_stats_t* stats, uint64_t elapsed_ns) {
    if (stats->count < stats->capacity) {
        stats->samples[stats->count++] = elapsed_ns;
    }
}

// Отримання поточного часу в наносекундах через POSIX CLOCK_MONOTONIC
static inline uint64_t get_monotonic_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

// Компаратор для швидкого сортування qsort
static int compare_uint64(const void* a, const void* b) {
    uint64_t arg1 = *(const uint64_t*)a;
    uint64_t arg2 = *(const uint64_t*)b;
    if (arg1 < arg2) return -1;
    if (arg1 > arg2) return 1;
    return 0;
}

// Розрахунок та вивід підсумкового звіту
void benchmark_stats_print_report(benchmark_stats_t* stats, const char* label) {
    if (stats->count == 0) {
        printf("[%s] Немає замірів для аналізу.\n", label);
        return;
    }

    // Сортування замірів для розрахунку перцентилів
    qsort(stats->samples, stats->count, sizeof(uint64_t), compare_uint64);

    uint64_t min_ns = stats->samples[0];
    uint64_t max_ns = stats->samples[stats->count - 1];
    
    double sum = 0.0;
    for (size_t i = 0; i < stats->count; ++i) {
        sum += (double)stats->samples[i];
    }
    double mean_ns = sum / (double)stats->count;

    // Розрахунок стандартного відхилення
    double variance_sum = 0.0;
    for (size_t i = 0; i < stats->count; ++i) {
        double diff = (double)stats->samples[i] - mean_ns;
        variance_sum += diff * diff;
    }
    double stddev_ns = sqrt(variance_sum / (double)stats->count);

    uint64_t p50 = stats->samples[(size_t)(stats->count * 0.50)];
    uint64_t p90 = stats->samples[(size_t)(stats->count * 0.90)];
    uint64_t p99 = stats->samples[(size_t)(stats->count * 0.99)];

    printf("=== Звіт бенчмарка: %s (вибірка: %zu вимірів) ===\n", label, stats->count);
    printf("  Мін:        %8.3f мкс\n", min_ns / 1000.0);
    printf("  Макс:       %8.3f мкс\n", max_ns / 1000.0);
    printf("  Середнє:    %8.3f мкс\n", mean_ns / 1000.0);
    printf("  StdDev:     %8.3f мкс\n", stddev_ns / 1000.0);
    printf("  P50 (Med):  %8.3f мкс\n", p50 / 1000.0);
    printf("  P90:        %8.3f мкс\n", p90 / 1000.0);
    printf("  P99:        %8.3f мкс\n", p99 / 1000.0);
}
