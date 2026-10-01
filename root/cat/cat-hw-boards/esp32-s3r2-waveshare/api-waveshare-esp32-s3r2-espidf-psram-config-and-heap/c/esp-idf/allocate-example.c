#include <stdio.h>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "PSRAM_ALLOC";

void allocate_example(void) {
    size_t psram_bytes = 1024 * 512; // 512 КБ
    uint8_t *frame_buffer = (uint8_t *)heap_caps_malloc(psram_bytes, MALLOC_CAP_SPIRAM);
    if (frame_buffer == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити 512 КБ у PSRAM");
        return;
    }

    size_t dma_bytes = 2048; // 2 КБ під DMA
    uint8_t *dma_buf = (uint8_t *)heap_caps_malloc(dma_bytes, MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA);
    if (dma_buf == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити DMA буфер у SRAM");
        heap_caps_free(frame_buffer);
        return;
    }

    ESP_LOGI(TAG, "Виділено: PSRAM=%p, DMA SRAM=%p", frame_buffer, dma_buf);

    heap_caps_free(frame_buffer);
    heap_caps_free(dma_buf);
}
