// Повний C-конвеєр з ручним виділенням пам'яті та goto cleanup
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef enum {
    STATUS_OK = 0,
    STATUS_FILE_ERROR,
    STATUS_PARSE_ERROR,
    STATUS_VALIDATION_ERROR
} AppStatus;

typedef struct {
    char host[64];
    int port;
} AppConfig;

AppStatus load_config_c(const char* path, AppConfig* cfg) {
    FILE* f = fopen(path, "r");
    if (!f) return STATUS_FILE_ERROR;

    char buf[128];
    if (!fgets(buf, sizeof(buf), f)) {
        fclose(f);
        return STATUS_FILE_ERROR;
    }
    fclose(f);

    if (sscanf(buf, "%63s %d", cfg->host, &cfg->port) != 2) {
        return STATUS_PARSE_ERROR;
    }

    if (cfg->port < 1 || cfg->port > 65535) {
        return STATUS_VALIDATION_ERROR;
    }

    return STATUS_OK;
}
