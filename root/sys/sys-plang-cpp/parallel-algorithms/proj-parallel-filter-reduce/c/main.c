#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <pthread.h>
#include <sys/time.h>

#define NUM_RECORDS 10000000
#define NUM_THREADS 8

typedef struct {
    uint32_t server_id;
    uint16_t status_code;
    uint32_t latency_us;
    uint32_t bytes_transferred;
} TelemetryRecord;

typedef struct {
    const TelemetryRecord* records;
    size_t start_idx;
    size_t end_idx;
    double partial_penalty;
    uint32_t max_latency;
} WorkerTask;

void* process_chunk(void* arg) {
    WorkerTask* task = (WorkerTask*)arg;
    double local_penalty = 0.0;
    uint32_t local_max_latency = 0;

    for (size_t i = task->start_idx; i < task->end_idx; ++i) {
        const TelemetryRecord* r = &task->records[i];
        if (r->latency_us > 5000 || r->status_code >= 500) {
            double penalty = 0.0;
            if (r->latency_us > 5000) {
                penalty += (r->latency_us - 5000) * 1.5;
            }
            penalty += (double)r->bytes_transferred / 1024.0;
            local_penalty += penalty;

            if (r->latency_us > local_max_latency) {
                local_max_latency = r->latency_us;
            }
        }
    }

    task->partial_penalty = local_penalty;
    task->max_latency = local_max_latency;
    return NULL;
}

int main(void) {
    TelemetryRecord* dataset = (TelemetryRecord*)malloc(sizeof(TelemetryRecord) * NUM_RECORDS);
    if (!dataset) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        return 1;
    }

    // Ініціалізація псевдовипадкових телеметричних даних
    for (size_t i = 0; i < NUM_RECORDS; ++i) {
        dataset[i].server_id = (uint32_t)(i % 128);
        dataset[i].status_code = (i % 50 == 0) ? 503 : 200;
        dataset[i].latency_us = (uint32_t)((i * 37) % 12000);
        dataset[i].bytes_transferred = (uint32_t)((i * 101) % 65536);
    }

    pthread_t threads[NUM_THREADS];
    WorkerTask tasks[NUM_THREADS];
    size_t chunk_size = NUM_RECORDS / NUM_THREADS;

    for (int t = 0; t < NUM_THREADS; ++t) {
        tasks[t].records = dataset;
        tasks[t].start_idx = t * chunk_size;
        tasks[t].end_idx = (t == NUM_THREADS - 1) ? NUM_RECORDS : (t + 1) * chunk_size;
        tasks[t].partial_penalty = 0.0;
        tasks[t].max_latency = 0;
        pthread_create(&threads[t], NULL, process_chunk, &tasks[t]);
    }

    double total_penalty = 0.0;
    uint32_t global_max_latency = 0;

    for (int t = 0; t < NUM_THREADS; ++t) {
        pthread_join(threads[t], NULL);
        total_penalty += tasks[t].partial_penalty;
        if (tasks[t].max_latency > global_max_latency) {
            global_max_latency = tasks[t].max_latency;
        }
    }

    printf("[C + pthreads] Разом штраф: %.2f | Макс затримка: %u мкс\n", 
           total_penalty, global_max_latency);

    free(dataset);
    return 0;
}
