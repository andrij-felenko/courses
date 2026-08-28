// config_safe.h
#ifndef CONFIG_SAFE_H
#define CONFIG_SAFE_H

typedef struct {
    int max_retries;
    int is_initialized;
} Config;

Config* get_config(void);

#endif // CONFIG_SAFE_H

// config_safe.c
#include "config_safe.h"

Config* get_config(void) {
    // У C локальний static ініціалізується нулями або константним виразом
    static Config instance = { .max_retries = 3, .is_initialized = 1 };
    return &instance;
}
