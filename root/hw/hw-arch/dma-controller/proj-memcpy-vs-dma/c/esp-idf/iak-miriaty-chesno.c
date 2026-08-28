#include <string.h>
#include "esp_cpu.h"
#include "esp_log.h"

static const char *TAG = "bench";

/* Буфери — 4-байтово вирівняні (копіювальник іде словами, не байтами) */
static uint8_t src[4096] __attribute__((aligned(4)));
static uint8_t dst[4096] __attribute__((aligned(4)));

/* Зчитати цикловий лічильник ядра */
static inline uint32_t cyc(void) {
    return esp_cpu_get_cycle_count();
}

/* Повертає кількість тактів, потрачених на memcpy(d, s, n) */
uint32_t bench_memcpy(void *d, const void *s, size_t n) {
    uint32_t t0 = cyc();
    memcpy(d, s, n);
    uint32_t t1 = cyc();
    return t1 - t0;   /* різниця тактів; про обгортання лічильника — нижче */
}

void app_main(void) {
    ESP_LOGI(TAG, "memcpy 4096 Б: %u тактів",
             (unsigned)bench_memcpy(dst, src, sizeof(src)));
}
