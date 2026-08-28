#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <math.h>
#include <time.h>

#define N 10000000
#define NUM_THREADS 4

typedef struct {
    double* data;
    size_t start;
    size_t end;
    double partial_sum;
} WorkerTask;

void* parallel_worker(void* arg) {
    WorkerTask* task = (WorkerTask*)arg;
    double sum = 0.0;
    /* Паралельна фаза: важкі математичні перетворення */
    for (size_t i = task->start; i < task->end; ++i) {
        task->data[i] = sqrt(task->data[i]) * 1.5;
        sum += task->data[i];
    }
    task->partial_sum = sum;
    return NULL;
}

int main(void) {
    double* array = (double*)malloc(sizeof(double) * N);
    for (size_t i = 0; i < N; ++i) array[i] = (double)i + 1.0;

    pthread_t threads[NUM_THREADS];
    WorkerTask tasks[NUM_THREADS];
    size_t chunk = N / NUM_THREADS;

    /* 1. Паралельна фаза Tp */
    for (int i = 0; i < NUM_THREADS; ++i) {
        tasks[i].data = array;
        tasks[i].start = i * chunk;
        tasks[i].end = (i == NUM_THREADS - 1) ? N : (i + 1) * chunk;
        pthread_create(&threads[i], NULL, parallel_worker, &tasks[i]);
    }

    double total_sum = 0.0;
    for (int i = 0; i < NUM_THREADS; ++i) {
        pthread_join(threads[i], NULL);
        total_sum += tasks[i].partial_sum;
    }

    /* 2. Послідовна фаза Ts: фінальна агрегація та верифікація */
    double serial_check = 0.0;
    for (size_t i = 0; i < N; i += 100) {
        serial_check += log(array[i]);
    }

    printf("Результат: sum = %.2f, check = %.2f\n", total_sum, serial_check);
    free(array);
    return 0;
}
