#include <stdio.h>
#include <stdlib.h>
#include <stdatomic.h>
#include <string.h>

typedef struct ConfigState {
    int timeout_ms;
    int max_connections;
    char mode[16];
} ConfigState;

_Atomic(const ConfigState*) global_config = NULL;

ConfigState* create_config(int timeout, int max_conn, const char* mode) {
    ConfigState* cfg = (ConfigState*)malloc(sizeof(ConfigState));
    cfg->timeout_ms = timeout;
    cfg->max_connections = max_conn;
    strncpy(cfg->mode, mode, sizeof(cfg->mode) - 1);
    cfg->mode[sizeof(cfg->mode) - 1] = '\0';
    return cfg;
}

const ConfigState* get_config(void) {
    return atomic_load_explicit(&global_config, memory_order_acquire);
}

void update_config(int new_timeout, int new_max_conn, const char* new_mode) {
    ConfigState* new_cfg = create_config(new_timeout, new_max_conn, new_mode);
    const ConfigState* old_cfg = atomic_load_explicit(&global_config, memory_order_relaxed);
    while (!atomic_compare_exchange_weak_explicit(
        &global_config, &old_cfg, new_cfg, memory_order_release, memory_order_relaxed));
}

int main(void) {
    printf("=== Lock-Free Copy-On-Write Config Container (C) ===\n");
    global_config = create_config(1000, 50, "NORMAL");

    const ConfigState* cfg1 = get_config();
    printf("Config: timeout=%d, max_conn=%d, mode=%s\n", cfg1->timeout_ms, cfg1->max_connections, cfg1->mode);

    update_config(2000, 100, "HIGH_PERF");

    const ConfigState* cfg2 = get_config();
    printf("Updated Config: timeout=%d, max_conn=%d, mode=%s\n", cfg2->timeout_ms, cfg2->max_connections, cfg2->mode);

    return 0;
}
