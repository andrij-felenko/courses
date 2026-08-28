#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <time.h>
#include <unistd.h>
#include <math.h>

#define MAX_RETRIES 3
#define BASE_BACKOFF_MS 100
#define MAX_BACKOFF_MS 10000

typedef struct {
    int status_code;
    int retry_after_sec;
    char body[512];
} http_response_t;

/* Генерація псевдо-UUIDv4 для заголовка Idempotency-Key */
void generate_idempotency_key(char *out_buf, size_t buf_sz) {
    snprintf(out_buf, buf_sz, "idemp-%08x-%04x-4%03x-a%03x-%08x",
             (unsigned int)rand(), (unsigned int)rand() & 0xFFFF,
             (unsigned int)rand() & 0x0FFF, (unsigned int)rand() & 0x0FFF,
             (unsigned int)rand());
}

/* Обчислення Full Jitter: Uniform(0, min(MAX, BASE * 2^i)) */
long compute_full_jitter_ms(int attempt, int retry_after_sec) {
    if (retry_after_sec > 0) {
        long base_ms = (long)retry_after_sec * 1000;
        long jitter = (rand() % 100); /* +0..99 мс */
        return base_ms + jitter;
    }
    long max_for_attempt = BASE_BACKOFF_MS * (1L << attempt);
    if (max_for_attempt > MAX_BACKOFF_MS) {
        max_for_attempt = MAX_BACKOFF_MS;
    }
    return (rand() % (max_for_attempt + 1));
}

/* Імітація мережевого запиту до сервера */
http_response_t mock_network_send(const char *method, const char *url, const char *idemp_key, int attempt) {
    http_response_t res;
    memset(&res, 0, sizeof(res));

    /* Симулюємо тимчасову помилку 503 на перших двох спробах */
    if (attempt < 2) {
        res.status_code = 503;
        res.retry_after_sec = 0;
        snprintf(res.body, sizeof(res.body), "{\"error\": \"Service Unavailable\"}");
    } else {
        res.status_code = 200;
        res.retry_after_sec = 0;
        snprintf(res.body, sizeof(res.body), "{\"status\": \"Processed successfully\", \"key\": \"%s\"}", idemp_key);
    }
    return res;
}

int http_post_with_retry(const char *url, const char *payload, http_response_t *out_response) {
    char idemp_key[64];
    generate_idempotency_key(idemp_key, sizeof(idemp_key));

    for (int attempt = 0; attempt <= MAX_RETRIES; ++attempt) {
        *out_response = mock_network_send("POST", url, idemp_key, attempt);

        if (out_response->status_code >= 200 && out_response->status_code < 300) {
            return 0; /* Успіх */
        }

        bool is_transient = (out_response->status_code == 429 ||
                             out_response->status_code == 502 ||
                             out_response->status_code == 503 ||
                             out_response->status_code == 504);

        if (!is_transient || attempt == MAX_RETRIES) {
            return -1; /* Фатальна помилка або вичерпано спроби */
        }

        long sleep_ms = compute_full_jitter_ms(attempt, out_response->retry_after_sec);
        usleep((useconds_t)(sleep_ms * 1000));
    }
    return -1;
}
