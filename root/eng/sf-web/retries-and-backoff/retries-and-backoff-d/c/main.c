#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <unistd.h>
#include <time.h>

#define MAX_RETRIES 3
#define BASE_BACKOFF_MS 100
#define MAX_BACKOFF_MS 10000

typedef struct {
    int status_code;
    int retry_after_sec;
    char body[256];
} http_raw_response_t;

/* Генерація псевдо-UUIDv4 для ключа ідемпотентності */
void generate_idempotency_uuid(char *buf, size_t sz) {
    snprintf(buf, sz, "%04x%04x-%04x-4%03x-8%03x-%04x%04x%04x",
             rand() & 0xFFFF, rand() & 0xFFFF, rand() & 0xFFFF,
             rand() & 0x0FFF, rand() & 0x0FFF,
             rand() & 0xFFFF, rand() & 0xFFFF, rand() & 0xFFFF);
}

/* Обчислення Full Jitter: Uniform(0, min(MAX, BASE * 2^i)) */
long calculate_full_jitter_ms(int attempt, int retry_after_sec) {
    if (retry_after_sec > 0) {
        return ((long)retry_after_sec * 1000) + (rand() % 150); /* +0..150 мс джитер */
    }
    long upper_bound = BASE_BACKOFF_MS * (1L << attempt);
    if (upper_bound > MAX_BACKOFF_MS) {
        upper_bound = MAX_BACKOFF_MS;
    }
    return (rand() % (upper_bound + 1));
}

/* Симуляція відправки HTTP-пакета через сокет */
http_raw_response_t mock_send_http(const char *method, const char *url,
                                   const char *idemp_key, int attempt) {
    http_raw_response_t res;
    memset(&res, 0, sizeof(res));

    /* Імітуємо відновлення сервера на третій спробі */
    if (attempt < 2) {
        res.status_code = 503;
        res.retry_after_sec = 0;
        snprintf(res.body, sizeof(res.body), "Service Unavailable");
    } else {
        res.status_code = 201;
        res.retry_after_sec = 0;
        snprintf(res.body, sizeof(res.body), "{\"status\":\"Created\",\"key\":\"%s\"}", idemp_key);
    }
    return res;
}

int execute_http_with_retry(const char *url, const char *payload, http_raw_response_t *out_res) {
    char idemp_key[40];
    generate_idempotency_uuid(idemp_key, sizeof(idemp_key));

    for (int attempt = 0; attempt <= MAX_RETRIES; ++attempt) {
        *out_res = mock_send_http("POST", url, idemp_key, attempt);

        if (out_res->status_code >= 200 && out_res->status_code < 300) {
            return 0; /* Успіх */
        }

        bool is_transient = (out_res->status_code == 429 ||
                             out_res->status_code == 502 ||
                             out_res->status_code == 503 ||
                             out_res->status_code == 504);

        if (!is_transient || attempt == MAX_RETRIES) {
            return -1; /* Фатальний код або вичерпано ліміт спроб */
        }

        long delay_ms = calculate_full_jitter_ms(attempt, out_res->retry_after_sec);
        usleep((useconds_t)(delay_ms * 1000));
    }
    return -1;
}
