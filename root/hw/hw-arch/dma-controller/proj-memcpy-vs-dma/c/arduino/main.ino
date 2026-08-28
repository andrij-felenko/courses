#include <Arduino.h>

/* Буфери — 4-байтово вирівняні (копіювальник іде словами, не байтами) */
static uint8_t src[4096] __attribute__((aligned(4)));
static uint8_t dst[4096] __attribute__((aligned(4)));

/* Зчитати цикловий лічильник ядра (плата на ESP32) */
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
