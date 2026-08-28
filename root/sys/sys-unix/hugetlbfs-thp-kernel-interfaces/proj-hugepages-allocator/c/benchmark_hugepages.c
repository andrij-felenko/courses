/* benchmark_hugepages.c — Реалізація мовою C із використанням POSIX API */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <sys/mman.h>
#include <unistd.h>

#define ALLOC_SIZE (256 * 1024 * 1024) // 256 МіБ
#define NUM_ACCESSES 10000000          // 10 млн випадкових звернень

typedef enum {
    MODE_STANDARD_4K,
    MODE_THP_MADVISE,
    MODE_HUGETLB_2M
} alloc_mode_t;

// Допоміжна функція для точного вимірювання часу у секундах
static double get_time_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
}

// Виділення пам'яті відповідно до обраного режиму
static uint8_t* allocate_buffer(alloc_mode_t mode) {
    uint8_t *ptr = NULL;

    switch (mode) {
        case MODE_STANDARD_4K:
            ptr = (uint8_t*)mmap(NULL, ALLOC_SIZE, PROT_READ | PROT_WRITE,
                                 MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
            if (ptr == MAP_FAILED) {
                perror("Помилка mmap (4K)");
                return NULL;
            }
            break;

        case MODE_THP_MADVISE:
            ptr = (uint8_t*)mmap(NULL, ALLOC_SIZE, PROT_READ | PROT_WRITE,
                                 MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
            if (ptr == MAP_FAILED) {
                perror("Помилка mmap (THP)");
                return NULL;
            }
            if (madvise(ptr, ALLOC_SIZE, MADV_HUGEPAGE) != 0) {
                perror("Попередження: madvise(MADV_HUGEPAGE) не вдалося");
            }
            break;

        case MODE_HUGETLB_2M:
            ptr = (uint8_t*)mmap(NULL, ALLOC_SIZE, PROT_READ | PROT_WRITE,
                                 MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB | MAP_HUGE_2MB,
                                 -1, 0);
            if (ptr == MAP_FAILED) {
                perror("Помилка mmap (HugeTLB 2M — перевірте vm.nr_hugepages)");
                return NULL;
            }
            break;
    }

    return ptr;
}

// Бенчмарк випадкового доступу до буфера
static void run_benchmark(const char *name, alloc_mode_t mode) {
    uint8_t *buffer = allocate_buffer(mode);
    if (!buffer) return;

    // 1. Прогрів пам'яті (ініціалізація сторінкових збоїв page fault)
    for (size_t i = 0; i < ALLOC_SIZE; i += 4096) {
        buffer[i] = 1;
    }

    // 2. Генерація псевдовипадкового обходу
    uint32_t seed = 0x12345678;
    double start_time = get_time_sec();

    volatile uint64_t sum = 0;
    size_t mask = ALLOC_SIZE - 1;

    for (size_t i = 0; i < NUM_ACCESSES; ++i) {
        // Простий генератор LCG для низьких накладних витрат CPU
        seed = seed * 1664525u + 1013904223u;
        size_t index = (size_t)seed & mask;
        sum += buffer[index];
        buffer[index] = (uint8_t)(sum & 0xFF);
    }

    double elapsed = get_time_sec() - start_time;
    double ns_per_access = (elapsed / NUM_ACCESSES) * 1e9;

    printf("[C] %-20s: Час = %.4f сек | Затримка = %.2f нс/доступ (sum=%lu)\n",
           name, elapsed, ns_per_access, (unsigned long)sum);

    munmap(buffer, ALLOC_SIZE);
}

int main(void) {
    printf("=== Вимірювач продуктивності пам'яті (256 МіБ, 10 млн операцій) ===\n");
    run_benchmark("Стандартні 4K", MODE_STANDARD_4K);
    run_benchmark("THP (madvise)", MODE_THP_MADVISE);
    run_benchmark("HugeTLB (2M)", MODE_HUGETLB_2M);
    return 0;
}
