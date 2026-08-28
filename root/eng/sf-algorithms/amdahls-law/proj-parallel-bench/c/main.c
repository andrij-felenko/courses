#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
#include <time.h>
#include <pthread.h>

#define CACHE_LINE 64
#define ARRAY_SIZE (32 * 1024 * 1024)   /* 32 мільйони елементів */
#define REPEAT_COUNT 4

/* Структура контексту потоку з вирівнюванням для уникнення false sharing */
typedef struct {
    double* data;
    size_t start_idx;
    size_t end_idx;
    double local_sum;
    uint8_t padding[CACHE_LINE - sizeof(double) - 2 * sizeof(size_t) - sizeof(double*)];
} thread_task_t;

/* Отримання поточного монотонного часу в секундах */
static double get_time_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
}

/* Паралельна робоча функція: інтенсивні математичні обчислення */
static void* worker_thread(void* arg) {
    thread_task_t* task = (thread_task_t*)arg;
    double sum = 0.0;
    for (size_t i = task->start_idx; i < task->end_idx; ++i) {
        double v = task->data[i];
        /* Штучне навантаження з плаваючою комою */
        for (int r = 0; r < REPEAT_COUNT; ++r) {
            v = sin(v) * cos(v) + sqrt(fabs(v) + 1.0);
        }
        task->data[i] = v;
        sum += v;
    }
    task->local_sum = sum;
    return NULL;
}

/* Послідовна фаза: фінальна збірка та додаткове послідовне навантаження */
static double serial_reduction(const double* data, size_t size, double partial_sum) {
    double acc = partial_sum;
    /* Послідовна обробка масиву для створення фіксованого Ts */
    for (size_t i = 0; i < size; i += 64) {
        acc += log(fabs(data[i]) + 1.0);
    }
    return acc;
}

/* Запуск одного експерименту на заданій кількості потоків */
static double run_experiment(double* data, size_t size, int num_threads) {
    pthread_t* threads = (pthread_t*)malloc(sizeof(pthread_t) * (size_t)num_threads);
    thread_task_t* tasks = (thread_task_t*)aligned_alloc(CACHE_LINE, sizeof(thread_task_t) * (size_t)num_threads);

    if (!threads || !tasks) {
        perror("Помилка виділення пам'яті");
        exit(EXIT_FAILURE);
    }

    size_t chunk_size = size / (size_t)num_threads;
    double t_start = get_time_sec();

    /* 1. Паралельна фаза: запуск потоків */
    for (int i = 0; i < num_threads; ++i) {
        tasks[i].data = data;
        tasks[i].start_idx = (size_t)i * chunk_size;
        tasks[i].end_idx = (i == num_threads - 1) ? size : tasks[i].start_idx + chunk_size;
        tasks[i].local_sum = 0.0;
        pthread_create(&threads[i], NULL, worker_thread, &tasks[i]);
    }

    /* Очікування завершення всіх потоків (бар'єрна синхронізація) */
    double parallel_sum = 0.0;
    for (int i = 0; i < num_threads; ++i) {
        pthread_join(threads[i], NULL);
        parallel_sum += tasks[i].local_sum;
    }

    /* 2. Послідовна фаза: виконується лише головним потоком */
    volatile double final_result = serial_reduction(data, size, parallel_sum);
    (void)final_result;

    double t_end = get_time_sec();

    free(tasks);
    free(threads);
    return t_end - t_start;
}

int main(void) {
    printf("=== Бенчмарк закону Амдала (C99 / pthreads) ===\n");
    printf("Розмір масиву: %zu елементів (%.1f МБ)\n\n",
           (size_t)ARRAY_SIZE, (double)(ARRAY_SIZE * sizeof(double)) / (1024.0 * 1024.0));

    double* data = (double*)malloc(sizeof(double) * ARRAY_SIZE);
    if (!data) {
        perror("Не вдалося виділити пам'ять під масив");
        return EXIT_FAILURE;
    }

    /* Ініціалізація даних */
    for (size_t i = 0; i < ARRAY_SIZE; ++i) {
        data[i] = (double)(i % 1000) * 0.001 + 0.1;
    }

    /* Базовий замір на 1 потоці (T1) */
    int test_threads[] = {1, 2, 4, 8, 16};
    int num_tests = sizeof(test_threads) / sizeof(test_threads[0]);

    printf("%-8s %-12s %-12s %-14s %-16s\n",
           "Потоки", "Час (с)", "Speedup S(N)", "Efficiency E(N)", "Karp-Flatt (e)");
    printf("----------------------------------------------------------------------\n");

    double t1 = run_experiment(data, ARRAY_SIZE, 1);
    printf("%-8d %-12.4f %-12.2f %-14.2f %-16s\n", 1, t1, 1.0, 1.0, "—");

    for (int idx = 1; idx < num_tests; ++idx) {
        int n = test_threads[idx];
        /* Відновлення початкового стану масиву */
        for (size_t i = 0; i < ARRAY_SIZE; ++i) {
            data[i] = (double)(i % 1000) * 0.001 + 0.1;
        }

        double tn = run_experiment(data, ARRAY_SIZE, n);
        double speedup = t1 / tn;
        double efficiency = speedup / (double)n;
        double e_metric = (1.0 / speedup - 1.0 / (double)n) / (1.0 - 1.0 / (double)n);

        printf("%-8d %-12.4f %-12.2f %-14.2f %-16.4f\n",
               n, tn, speedup, efficiency, e_metric);
    }

    free(data);
    return EXIT_SUCCESS;
}
