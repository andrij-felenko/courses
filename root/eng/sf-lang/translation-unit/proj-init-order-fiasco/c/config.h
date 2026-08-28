// config.h
#ifndef CONFIG_H
#define CONFIG_H

typedef struct {
    int max_retries;
    int is_initialized;
} Config;

extern Config g_config;
void config_init(void);

#endif // CONFIG_H
