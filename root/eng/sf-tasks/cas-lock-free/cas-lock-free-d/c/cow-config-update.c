#include <stdatomic.h>
#include <pthread.h>
#include <stdlib.h>
#include <string.h>

// 1. Оновлення конфігурації через CAS + Copy-on-Write (для Read-Heavy)
typedef struct {
    char host[64];
    int port;
} config_t;

typedef struct {
    _Atomic(config_t*) ptr;
} cow_config_t;

void cow_config_update(cow_config_t* cfg, const char* new_host, int new_port) {
    config_t* new_cfg = malloc(sizeof(config_t));
    strncpy(new_cfg->host, new_host, sizeof(new_cfg->host));
    new_cfg->port = new_port;

    config_t* old_cfg = atomic_load_explicit(&cfg->ptr, memory_order_relaxed);
    while (!atomic_compare_exchange_weak_explicit(
        &cfg->ptr, &old_cfg, new_cfg,
        memory_order_release, memory_order_relaxed)) {}
}

// 2. Оновлення складного стану через Mutex (для Write-Heavy або великих даних)
typedef struct {
    pthread_mutex_t lock;
    int table[1024];
} mutex_state_t;

void mutex_state_update(mutex_state_t* st, int index, int val) {
    pthread_mutex_lock(&st->lock);
    st->table[index] = val;
    pthread_mutex_unlock(&st->lock);
}
