#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <semaphore.h>
#include <math.h>
#include <unistd.h>

/* В аналогічній POSIX C реалізації доводиться поєднувати
   pthread_barrier_t та sem_t, контролюючи фазовий swap вручну */

#define GRID_H 256
#define GRID_W 256
#define NUM_WORKERS 4
#define NUM_STEPS 5

float g_buf_a[GRID_H * GRID_W];
float g_buf_b[GRID_H * GRID_W];
float* g_in = g_buf_a;
float* g_out = g_buf_b;

pthread_barrier_t g_barrier;
sem_t g_log_sem;

typedef struct {
    int id;
    size_t start_row;
    size_t end_row;
} worker_args_t;

void* posix_worker_task(void* arg) {
    worker_args_t* args = (worker_args_t*)arg;

    for (int step = 0; step < NUM_STEPS; ++step) {
        for (size_t y = args->start_row; y < args->end_row; ++y) {
            for (size_t x = 1; x < GRID_W - 1; ++x) {
                size_t idx = y * GRID_W + x;
                float up = g_in[(y - 1) * GRID_W + x];
                float down = g_in[(y + 1) * GRID_W + x];
                float left = g_in[y * GRID_W + (x - 1)];
                float right = g_in[y * GRID_W + (x + 1)];
                g_out[idx] = 0.25f * (up + down + left + right);
            }
        }

        // Синхронізація на бар'єрі POSIX
        int rc = pthread_barrier_wait(&g_barrier);
        if (rc == PTHREAD_BARRIER_SERIAL_THREAD) {
            float* tmp = g_in;
            g_in = g_out;
            g_out = tmp;
            printf("[POSIX] Крок %d завершено, буфери обміняно.\n", step + 1);
        }
    }
    return NULL;
}
