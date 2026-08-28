#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
#include <stdlib.h>
#include <string.h>

#define CACHE_LINE_SIZE 64

/* Структура одного шарду, вирівняна за розміром кеш-лінії */
typedef struct {
    _Atomic uint64_t value;
    uint8_t padding[CACHE_LINE_SIZE - sizeof(_Atomic uint64_t)];
} __attribute__((aligned(CACHE_LINE_SIZE))) counter_shard_t;

typedef struct {
    counter_shard_t* shards;
    size_t num_shards;
    size_t mask; /* num_shards має бути степенем двійки */
} sharded_counter_t;

sharded_counter_t* sharded_counter_create(size_t num_shards) {
    size_t power = 1;
    while (power < num_shards) {
        power <<= 1;
    }

    sharded_counter_t* counter = (sharded_counter_t*)malloc(sizeof(sharded_counter_t));
    if (!counter) return NULL;

    /* Виділення динамічної пам'яті з вирівнюванням на межу 64 байтів */
    int ret = posix_memalign((void**)&counter->shards, CACHE_LINE_SIZE, power * sizeof(counter_shard_t));
    if (ret != 0) {
        free(counter);
        return NULL;
    }

    memset(counter->shards, 0, power * sizeof(counter_shard_t));
    counter->num_shards = power;
    counter->mask = power - 1;
    return counter;
}

void sharded_counter_add(sharded_counter_t* counter, size_t thread_id, uint64_t delta) {
    size_t slot = thread_id & counter->mask;
    atomic_fetch_add_explicit(&counter->shards[slot].value, delta, memory_order_relaxed);
}

uint64_t sharded_counter_get(const sharded_counter_t* counter) {
    uint64_t total = 0;
    for (size_t i = 0; i < counter->num_shards; ++i) {
        total += atomic_load_explicit(&counter->shards[i].value, memory_order_relaxed);
    }
    return total;
}

void sharded_counter_destroy(sharded_counter_t* counter) {
    if (counter) {
        free(counter->shards);
        free(counter);
    }
}
