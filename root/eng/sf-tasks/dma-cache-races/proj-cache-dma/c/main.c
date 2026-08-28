#include <stdlib.h>
#include <string.h>
#include "esp_heap_caps.h"
#include "esp_cache.h"           /* esp_cache_msync — IDF v5.x */

/* ── Розмір кешлінії ESP32-S3 ─────────────────────────────────────── */
#define CACHE_LINE  32u          /* байти */

/* ── Округлення розміру вгору до кратного CACHE_LINE ─────────────── */
/* size_round = (n + CACHE_LINE - 1) / CACHE_LINE * CACHE_LINE        */
#define ALIGN_UP(n, a)  (((n) + (a) - 1u) / (a) * (a))

/* ── Блок 1: виділення DMA-придатного, вирівняного буфера ────────── */
static uint8_t *dma_buf = NULL;
static size_t   dma_buf_sz = 0;

void audio_rx_init(size_t frame_bytes)
{
    /* Доповнюємо до кратного CACHE_LINE — «хвіст» не ділить лінію */
    dma_buf_sz = ALIGN_UP(frame_bytes, CACHE_LINE);

    /* heap_caps_aligned_alloc: початок — на межі CACHE_LINE         */
    /* MALLOC_CAP_DMA: PSRAM-регіон, доступний DMA-контролеру        */
    dma_buf = heap_caps_aligned_alloc(CACHE_LINE, dma_buf_sz,
                                      MALLOC_CAP_SPIRAM | MALLOC_CAP_DMA);
    /* NULL — не вистачило пам'яті; перевіряйте у реальному коді     */
}

/* ── Блок 2: приймання (RX) — invalidate ПІСЛЯ DMA, ДО читання ─── */
void audio_rx_read(void)
{
    /* 1. Чекаємо завершення DMA-транзакції (деталі — у §4.9.3)      */
    /* ... дочекалися переривання або перевірили прапорець ...        */

    /* 2. Інвалідуємо кешлінії буфера: пам'ять → кеш (M2C).          */
    /*    Альтернативний низькорівневий шлях: Cache_Invalidate_Addr() */
    esp_cache_msync(dma_buf, dma_buf_sz,
                    ESP_CACHE_MSYNC_FLAG_DIR_M2C);   /* invalidate    */

    /* 3. Тепер читаємо: кеш порожній → ядро йде в RAM і бере свіже  */
    process_audio(dma_buf, dma_buf_sz);
}

/* ── Блок 3: передавання (TX) — write-back ДО старту DMA ──────────  */
void audio_tx_send(const uint8_t *data, size_t len)
{
    /* 1. Заповнюємо буфер: записи ідуть у кеш (write-back політика) */
    memcpy(dma_buf, data, len);

    /* 2. Write-back (clean): кеш → пам'ять (C2M).                   */
    /*    Робимо ДО старту DMA — DMA побачить свіже в RAM             */
    esp_cache_msync(dma_buf, dma_buf_sz,
                    ESP_CACHE_MSYNC_FLAG_DIR_C2M);   /* write-back    */

    /* 3. Лише тепер запускаємо DMA-передачу                         */
    start_dma_tx(dma_buf, dma_buf_sz);
}
