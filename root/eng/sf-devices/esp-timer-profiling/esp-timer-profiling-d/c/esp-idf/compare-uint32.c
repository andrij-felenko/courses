#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include "esp_cpu.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define NUM_RUNS 100

// Компаратор для qsort при обчисленні медіани
static int compare_uint32(const void *a, const void *b) {
    uint32_t arg1 = *(const uint32_t *)a;
    uint32_t arg2 = *(const uint32_t *)b;
    if (arg1 < arg2) return -1;
    if (arg1 > arg2) return 1;
    return 0;
}

void profile_with_isolation_and_stats(void) {
    uint32_t samples[NUM_RUNS];
    portMUX_TYPE spinlock = portMUX_INITIALIZER_UNLOCKED;

    // Прогрів кєш-пам'яті (Warm-up run)
    volatile int dummy = 0;
    for (int i = 0; i < 100; i++) dummy += i;

    for (int r = 0; r < NUM_RUNS; r++) {
        // Ізоляція ділянки коду від витіснення та переривань
        taskENTER_CRITICAL(&spinlock);
        
        // Бар'єр пам'яті компілятора до заміру
        __asm__ __volatile__("" ::: "memory");
        uint32_t start = esp_cpu_get_cycle_count();
        
        // Вимірюваний алгоритм
        for (int i = 0; i < 200; i++) {
            dummy += (i ^ 0x5A);
        }
        
        // Бар'єр пам'яті компілятора після заміру
        __asm__ __volatile__("" ::: "memory");
        uint32_t end = esp_cpu_get_cycle_count();
        
        taskEXIT_CRITICAL(&spinlock);
        
        samples[r] = end - start;
    }

    // Сортування результатів для статистичного аналізу
    qsort(samples, NUM_RUNS, sizeof(uint32_t), compare_uint32);

    uint32_t min_val = samples[0];
    uint32_t max_val = samples[NUM_RUNS - 1];
    uint32_t median_val = samples[NUM_RUNS / 2];
    uint32_t p95_val = samples[(int)(NUM_RUNS * 0.95)];

    printf("Stats over %d runs (cycles):\n", NUM_RUNS);
    printf("  Min (pure execution): %lu\n", (unsigned long)min_val);
    printf("  Median:               %lu\n", (unsigned long)median_val);
    printf("  P95 (jitter tail):    %lu\n", (unsigned long)p95_val);
    printf("  Max (worst spike):    %lu\n", (unsigned long)max_val);
}
