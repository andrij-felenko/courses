#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <pthread.h>
#include <sched.h>
#include <time.h>
#include <unistd.h>

#define L1_TEST_SIZE (24 * 1024) // 24 КБ на потік
#define ITERATIONS   (25000000)  // Кількість ітерацій випадкового доступу

typedef struct {
    int cpu_id;
    size_t iterations;
    uint8_t *buffer;
    size_t buffer_size;
    double elapsed_ms;
} thread_arg_t;

static inline double get_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1000.0 + (double)ts.tv_nsec / 1000000.0;
}

// Функція навантаження: інтенсивне читання й запис у буфер кешу L1D
void* cache_thrashing_worker(void *arg) {
    thread_arg_t *tdata = (thread_arg_t*)arg;

    // Прив'язка поточної нитки до заданого логічного CPU
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(tdata->cpu_id, &cpuset);
    if (pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset) != 0) {
        perror("pthread_setaffinity_np");
        return NULL;
    }

    uint8_t *buf = tdata->buffer;
    size_t sz = tdata->buffer_size;
    size_t mask = sz - 1;

    double t_start = get_time_ms();

    uint32_t val = 0x12345678;
    size_t idx = 0;
    for (size_t i = 0; i < tdata->iterations; ++i) {
        // Псевдовипадковий кроковий доступ через лінійний конгруентний генератор
        idx = (idx * 1103515245 + 12345) & mask;
        buf[idx] ^= (uint8_t)(val & 0xFF);
        val = (val >> 1) | (val << 31);
    }

    double t_end = get_time_ms();
    tdata->elapsed_ms = t_end - t_start;
    return NULL;
}

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <cpu_id_0> <cpu_id_1>
", argv[0]);
        fprintf(stderr, "  Спільне ядро SMT:   %s 0 1
", argv[0]);
        fprintf(stderr, "  Окремі ядра:        %s 0 2
", argv[0]);
        return 1;
    }

    int cpu0 = atoi(argv[1]);
    int cpu1 = atoi(argv[2]);

    uint8_t *buf0 = (uint8_t*)aligned_alloc(64, L1_TEST_SIZE);
    uint8_t *buf1 = (uint8_t*)aligned_alloc(64, L1_TEST_SIZE);
    if (!buf0 || !buf1) {
        perror("aligned_alloc");
        return 1;
    }

    for (size_t i = 0; i < L1_TEST_SIZE; ++i) {
        buf0[i] = (uint8_t)(i & 0xFF);
        buf1[i] = (uint8_t)((i * 3) & 0xFF);
    }

    pthread_t th0, th1;
    thread_arg_t args[2] = {
        { .cpu_id = cpu0, .iterations = ITERATIONS, .buffer = buf0, .buffer_size = L1_TEST_SIZE, .elapsed_ms = 0 },
        { .cpu_id = cpu1, .iterations = ITERATIONS, .buffer = buf1, .buffer_size = L1_TEST_SIZE, .elapsed_ms = 0 }
    };

    printf("=== Запуск тесту на CPU %d та CPU %d ===
", cpu0, cpu1);
    double global_start = get_time_ms();

    pthread_create(&th0, NULL, cache_thrashing_worker, &args[0]);
    pthread_create(&th1, NULL, cache_thrashing_worker, &args[1]);

    pthread_join(th0, NULL);
    pthread_join(th1, NULL);

    double global_end = get_time_ms();

    printf("Нитка 0 (CPU %d): %.2f мс
", cpu0, args[0].elapsed_ms);
    printf("Нитка 1 (CPU %d): %.2f мс
", cpu1, args[1].elapsed_ms);
    printf("Загальний час виконання: %.2f мс
", global_end - global_start);

    free(buf0);
    free(buf1);
    return 0;
}
