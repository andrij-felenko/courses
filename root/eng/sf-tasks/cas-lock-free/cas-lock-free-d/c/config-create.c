#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdatomic.h>

// Багатополевий об'єкт конфігурації (незмінний після створення)
typedef struct {
    char host[64];
    int port;
    int max_connections;
} config_t;

typedef struct {
    _Atomic(config_t*) root;
} config_holder_t;

// Створення нової конфігурації
config_t* config_create(const char* host, int port, int max_conn) {
    config_t* cfg = (config_t*)malloc(sizeof(config_t));
    if (!cfg) return NULL;
    strncpy(cfg->host, host, sizeof(cfg->host) - 1);
    cfg->host[sizeof(cfg->host) - 1] = '\0';
    cfg->port = port;
    cfg->max_connections = max_conn;
    return cfg;
}

// Атомарне оновлення конфігурації через Copy-on-Write та CAS
void config_update_port(config_holder_t* holder, int new_port) {
    config_t* old_cfg = atomic_load_explicit(&holder->root, memory_order_relaxed);
    config_t* new_cfg = NULL;

    do {
        if (new_cfg) free(new_cfg); // Очищення невдалої копії перед повторною спробою
        
        // Крок 1 і 2: Копіювання та локальна модифікація
        new_cfg = config_create(old_cfg->host, new_port, old_cfg->max_connections);
        
        // Крок 3: Атомарна підміна root-вказівника
    } while (!atomic_compare_exchange_weak_explicit(
        &holder->root,
        &old_cfg,
        new_cfg,
        memory_order_release,
        memory_order_relaxed
    ));

    // Примітка: old_cfg не можна негайно free(), бо його можуть читати інші потоки!
}
