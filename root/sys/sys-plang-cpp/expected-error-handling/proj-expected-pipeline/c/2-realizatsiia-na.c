#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <stdbool.h>

// Типи помилок підсистеми
typedef enum {
    CONFIG_SUCCESS = 0,
    CONFIG_ERR_FILE_NOT_FOUND,
    CONFIG_ERR_READ_FAILED,
    CONFIG_ERR_PARSE_INVALID_PORT,
    CONFIG_ERR_PARSE_INVALID_THREADS,
    CONFIG_ERR_OUT_OF_MEMORY
} ConfigStatus;

// Структура налаштувань сервісу
typedef struct {
    char db_host[128];
    int port;
    int worker_threads;
} ServiceConfig;

// 1. Зчитування файлу конфігурації
ConfigStatus read_config_file(const char* filepath, char** out_buffer) {
    if (!filepath || !out_buffer) return CONFIG_ERR_READ_FAILED;

    FILE* f = fopen(filepath, "r");
    if (!f) {
        if (errno == ENOENT) return CONFIG_ERR_FILE_NOT_FOUND;
        return CONFIG_ERR_READ_FAILED;
    }

    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    fseek(f, 0, SEEK_SET);

    if (size <= 0) {
        fclose(f);
        return CONFIG_ERR_READ_FAILED;
    }

    char* buf = (char*)malloc((size_t)size + 1);
    if (!buf) {
        fclose(f);
        return CONFIG_ERR_OUT_OF_MEMORY;
    }

    size_t read_bytes = fread(buf, 1, (size_t)size, f);
    fclose(f);

    if (read_bytes != (size_t)size) {
        free(buf);
        return CONFIG_ERR_READ_FAILED;
    }

    buf[size] = '\0';
    *out_buffer = buf;
    return CONFIG_SUCCESS;
}

// 2. Парсинг та валідація вмісту
ConfigStatus parse_and_validate(const char* buffer, ServiceConfig* out_config) {
    if (!buffer || !out_config) return CONFIG_ERR_READ_FAILED;

    int port = 0;
    int threads = 0;
    char host[128] = {0};

    // Приклад спрощеного парсингу рядка format: host;port;threads
    int parsed = sscanf(buffer, "%127[^;];%d;%d", host, &port, &threads);
    if (parsed != 3) {
        return CONFIG_ERR_PARSE_INVALID_PORT;
    }

    // Валідація порту
    if (port < 1 || port > 65535) {
        return CONFIG_ERR_PARSE_INVALID_PORT;
    }

    // Валідація потоків
    if (threads < 1 || threads > 128) {
        return CONFIG_ERR_PARSE_INVALID_THREADS;
    }

    strncpy(out_config->db_host, host, sizeof(out_config->db_host) - 1);
    out_config->port = port;
    out_config->worker_threads = threads;

    return CONFIG_SUCCESS;
}

// Повний конвеєр з обробленням помилок через goto
ConfigStatus initialize_service_c(const char* config_path, ServiceConfig* out_cfg) {
    char* raw_buffer = NULL;
    ConfigStatus status = read_config_file(config_path, &raw_buffer);
    if (status != CONFIG_SUCCESS) {
        goto cleanup;
    }

    status = parse_and_validate(raw_buffer, out_cfg);
    if (status != CONFIG_SUCCESS) {
        goto cleanup;
    }

cleanup:
    if (raw_buffer) {
        free(raw_buffer);
    }
    return status;
}
