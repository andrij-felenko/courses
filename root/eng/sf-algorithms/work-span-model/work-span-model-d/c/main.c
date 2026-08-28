#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

#define CUTOFF_THRESHOLD 5000

typedef struct ReduceTask {
    const double *array;
    size_t start;
    size_t end;
    double result;
} ReduceTask;

void* parallel_sum_worker(void *arg) {
    ReduceTask *task = (ReduceTask*)arg;
    size_t length = task->end - task->start;

    // Базовий послідовний випадок для малих підмасивів
    if (length <= CUTOFF_THRESHOLD) {
        double sum = 0.0;
        for (size_t i = task->start; i < task->end; ++i) {
            sum += task->array[i];
        }
        task->result = sum;
        return NULL;
    }

    size_t mid = task->start + length / 2;

    // Ліва підзадача (spawn в окремий потік)
    ReduceTask left_task = { task->array, task->start, mid, 0.0 };
    ReduceTask right_task = { task->array, mid, task->end, 0.0 };

    pthread_t thread_left;
    pthread_create(&thread_left, NULL, parallel_sum_worker, &left_task);

    // Права підзадача виконується поточним потоком
    parallel_sum_worker(&right_task);

    // Синхронізація (sync / join)
    pthread_join(thread_left, NULL);

    task->result = left_task.result + right_task.result;
    return NULL;
}

double compute_total_sum(const double *arr, size_t size) {
    ReduceTask root_task = { arr, 0, size, 0.0 };
    parallel_sum_worker(&root_task);
    return root_task.result;
}
