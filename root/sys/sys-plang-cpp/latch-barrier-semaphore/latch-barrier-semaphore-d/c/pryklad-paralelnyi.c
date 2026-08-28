#include <stdio.h>
#include <pthread.h>
#include <stdlib.h>

/* У стандартному C POSIX надає pthread_barrier_t,
   але він не має вбудованого completion callback */
#define NUM_THREADS 4
#define NUM_STEPS 3

pthread_barrier_t g_barrier;
float buffer_a[1024];
float buffer_b[1024];
float* current_in = buffer_a;
float* current_out = buffer_b;

void* worker(void* arg) {
    long id = (long)arg;
    size_t chunk_size = 1024 / NUM_THREADS;
    size_t start = id * chunk_size;
    size_t end = start + chunk_size;

    for (int step = 0; step < NUM_STEPS; ++step) {
        for (size_t i = start; i < end; ++i) {
            current_out[i] = current_in[i] * 0.95f;
        }

        // PTHREAD_BARRIER_SERIAL_THREAD повертається рівно одному потоку
        int rc = pthread_barrier_wait(&g_barrier);
        if (rc == PTHREAD_BARRIER_SERIAL_THREAD) {
            float* tmp = current_in;
            current_in = current_out;
            current_out = tmp;
            printf("[POSIX Barrier] Крок %d завершено.\n", step + 1);
        }
        // Потрібен ДРУГИЙ бар'єр, щоб інші потоки не почали
        // читати current_in ДО того, як серійний потік завершить swap!
    }
    return NULL;
}
