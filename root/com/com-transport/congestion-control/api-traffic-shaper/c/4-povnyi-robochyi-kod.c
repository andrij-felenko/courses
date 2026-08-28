#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint64_t cir_bytes_per_sec;
    uint64_t cbs_bytes;
    size_t max_queue_bytes;
} shaper_config_t;

typedef struct {
    shaper_config_t config;
    double tokens;
    size_t current_queue_bytes;
    uint64_t last_update_us;
} shaper_t;

shaper_t* shaper_create(const shaper_config_t *config) {
    if (!config || config->cir_bytes_per_sec == 0 || config->cbs_bytes == 0) {
        return NULL;
    }
    shaper_t *s = (shaper_t*)malloc(sizeof(shaper_t));
    if (!s) return NULL;

    s->config = *config;
    s->tokens = (double)config->cbs_bytes;
    s->current_queue_bytes = 0;
    s->last_update_us = 0;
    return s;
}

void shaper_destroy(shaper_t *s) {
    if (s) free(s);
}

void shaper_update_tokens(shaper_t *s, uint64_t now_us) {
    if (s->last_update_us == 0) {
        s->last_update_us = now_us;
        return;
    }
    uint64_t elapsed = now_us - s->last_update_us;
    s->last_update_us = now_us;

    double added = ((double)elapsed * (double)s->config.cir_bytes_per_sec) / 1000000.0;
    s->tokens += added;
    if (s->tokens > (double)s->config.cbs_bytes) {
        s->tokens = (double)s->config.cbs_bytes;
    }
}

int shaper_process_packet(shaper_t *s, size_t packet_len, uint64_t now_us) {
    shaper_update_tokens(s, now_us);

    double len = (double)packet_len;
    if (s->tokens >= len) {
        s->tokens -= len;
        return 0; // SHAPER_OK
    }

    if (s->current_queue_bytes + packet_len > s->config.max_queue_bytes) {
        return -1; // SHAPER_DROP_FULL
    }

    s->current_queue_bytes += packet_len;
    return 1; // SHAPER_QUEUED
}

int main(void) {
    shaper_config_t cfg = {
        .cir_bytes_per_sec = 100000, // 100 КБ/с
        .cbs_bytes = 10000,          // 10 КБ сплеск
        .max_queue_bytes = 50000
    };

    shaper_t *s = shaper_create(&cfg);
    if (!s) {
        printf("Помилка створення шейпера\n");
        return 1;
    }

    uint64_t time_us = 0;
    printf("Старт: Жетонів = %.0f B\n", s->tokens);

    // Відправляємо пакет 8000 B
    int res1 = shaper_process_packet(s, 8000, time_us);
    printf("Пакет 1 (8000 B): результат = %d, залишок жетонів = %.0f B\n", res1, s->tokens);

    // Відправляємо другий пакет 5000 B при нехватці жетонів
    int res2 = shaper_process_packet(s, 5000, time_us);
    printf("Пакет 2 (5000 B): результат = %d, залишок жетонів = %.0f B\n", res2, s->tokens);

    // Прокручуємо час на 50 мс (50000 мкс) -> додається 5000 B жетонів
    time_us += 50000;
    int res3 = shaper_process_packet(s, 5000, time_us);
    printf("Пакет 3 через 50 мс (5000 B): результат = %d, залишок жетонів = %.0f B\n", res3, s->tokens);

    shaper_destroy(s);
    return 0;
}
