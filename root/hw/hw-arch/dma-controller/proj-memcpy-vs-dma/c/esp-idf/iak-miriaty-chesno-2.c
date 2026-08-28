#include "esp_async_memcpy.h"

/* Одноразове налаштування драйвера (виконується один раз при старті) */
static async_memcpy_handle_t mcp_handle;

void dma_init(void) {
    async_memcpy_config_t cfg = ASYNC_MEMCPY_DEFAULT_CONFIG();
    esp_async_memcpy_install(&cfg, &mcp_handle);
}

/* Прапорець готовності — volatile: колбек виконується в ISR */
static volatile bool dma_done;

/* Колбек готовності — IRAM_ATTR обов'язковий: виконується в перериванні */
static bool IRAM_ATTR dma_cb(async_memcpy_handle_t h,
                              async_memcpy_event_t *e, void *arg) {
    dma_done = true;
    return false;   /* false = не будити вищепріоритетну задачу */
}

/* Повертає повний час "старт → готовність" у тактах (включаючи busy-wait) */
uint32_t bench_dma(void *d, void *s, size_t n) {
    dma_done = false;
    uint32_t t0 = cyc();
    esp_async_memcpy(mcp_handle, d, s, n, dma_cb, NULL);
    while (!dma_done) {}       /* busy-wait: ядро чекає завершення */
    uint32_t t1 = cyc();
    return t1 - t0;
}
