#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>
#include <inttypes.h>

#define TEST_ITERATIONS 50000000ULL

// Невирівняна структура, що примусово перетинає межу кеш-лінії
typedef struct {
    char offset_padding[60];
    uint64_t counter;
} __attribute__((packed)) shared_payload_t;

static shared_payload_t g_payload;
static volatile bool g_active = true;
static uint64_t g_total_torn_reads = 0;

void *producer_worker(void *arg) {
    (void)arg;
    const uint64_t pattern_low = 0x0000000000000000ULL;
    const uint64_t pattern_high = 0xFFFFFFFFFFFFFFFFULL;

    for (uint64_t i = 0; i < TEST_ITERATIONS && g_active; ++i) {
        g_payload.counter = (i & 1) ? pattern_low : pattern_high;
    }
    g_active = false;
    return NULL;
}

void *consumer_worker(void *arg) {
    (void)arg;
    const uint64_t pattern_low = 0x0000000000000000ULL;
    const uint64_t pattern_high = 0xFFFFFFFFFFFFFFFFULL;
    uint64_t local_torn_hits = 0;

    while (g_active) {
        uint64_t val = g_payload.counter;
        if (val != pattern_low && val != pattern_high) {
            local_torn_hits++;
        }
    }

    __sync_fetch_and_add(&g_total_torn_reads, local_torn_hits);
    return NULL;
}

int main(void) {
    pthread_t writer_thread;
    pthread_t reader_threads[4];

    printf("Запуск перевірки неатомарного доступу...\n");

    pthread_create(&writer_thread, NULL, producer_worker, NULL);
    for (int i = 0; i < 4; ++i) {
        pthread_create(&reader_threads[i], NULL, consumer_worker, NULL);
    }

    pthread_join(writer_thread, NULL);
    for (int i = 0; i < 4; ++i) {
        pthread_join(reader_threads[i], NULL);
    }

    printf("Виявлено розривних станів пам'яті: %" PRIu64 "\n", g_total_torn_reads);
    return 0;
}
