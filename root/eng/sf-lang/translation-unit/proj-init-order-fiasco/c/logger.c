// logger.c
#include "config.h"
#include <stdio.h>

Config g_config;

void config_init(void) {
    g_config.max_retries = 3;
    g_config.is_initialized = 1;
}

void log_message(const char* msg) {
    if (!g_config.is_initialized) {
        fprintf(stderr, "FATAL: config is not initialized yet!\n");
        return;
    }
    printf("%s (retries=%d)\n", msg, g_config.max_retries);
}
