#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>
#include <unistd.h>
#include <inttypes.h>

#define ITERATIONS 100000000ULL

// Спеціально невирівняний буфер: зміщення 61 байт гарантує,
// що 8-байтне число перетинає межу 64-байтової кеш-лінії L1
typedef struct {
    char padding[61];
    uint64_t value;
} __attribute__((packed)) unaligned_payload_t;

typedef struct {
    unaligned_payload_t shared_data;
    volatile bool is_active;
    uint64_t total_torn_events;
} benchmark_env_t;

static benchmark_env_t g_env;

void *writer_thread(void *arg) {
    (void)arg;
    const uint64_t val_a = 0x0000000000000000ULL;
    const uint64_t val_b = 0xFFFFFFFFFFFFFFFFULL;

    for (uint64_t i = 0; i < ITERATIONS && g_env.is_active; ++i) {
        // Чергування запису двох патернів без атоміків над невирівняною пам'яттю
        g_env.shared_data.value = (i & 1) ? val_a : val_b;
    }
    g_env.is_active = false;
    return NULL;
}

void *reader_thread(void *arg) {
    (void)arg;
    const uint64_t val_a = 0x0000000000000000ULL;
    const uint64_t val_b = 0xFFFFFFFFFFFFFFFFULL;
    uint64_t local_torn = 0;

    while (g_env.is_active) {
        uint64_t sample = g_env.shared_data.value;
        // Якщо прочитано не 0 і не повну маску — це розривне читання!
        if (sample != val_a && sample != val_b) {
            local_torn++;
        }
    }

    __sync_fetch_and_add(&g_env.total_torn_events, local_torn);
    return NULL;
}

int main(void) {
    pthread_t writer;
    pthread_t readers[4];

    g_env.is_active = true;
    g_env.total_torn_events = 0;

    printf("Запуск стрес-тесту неатомарного доступу...\n");

    pthread_create(&writer, NULL, writer_thread, NULL);
    for (int i = 0; i < 4; ++i) {
        pthread_create(&readers[i], NULL, reader_thread, NULL);
    }

    pthread_join(writer, NULL);
    for (int i = 0; i < 4; ++i) {
        pthread_join(readers[i], NULL);
    }

    printf("Тест завершено. Виявлено розривних читань: %" PRIu64 "\n", g_env.total_torn_events);
    return 0;
}
