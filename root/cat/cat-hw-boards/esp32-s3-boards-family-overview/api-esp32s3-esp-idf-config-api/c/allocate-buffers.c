#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "mem_app";

void allocate_buffers(void) {
    // Виділення кадрового буфера 1 МБ у зовнішній PSRAM
    uint8_t *fb = (uint8_t *)heap_caps_malloc(1024 * 1024, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    if (fb == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити пам'ять у PSRAM!");
        return;
    }

    // Виділення буфера DMA 4 КБ у внутрішній SRAM
    uint8_t *dma_buf = (uint8_t *)heap_caps_malloc(4096, MALLOC_CAP_DMA | MALLOC_CAP_INTERNAL);
    if (dma_buf == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити DMA буфер у внутрішній SRAM!");
        heap_caps_free(fb);
        return;
    }

    // Звільнення виділеної пам'яті
    heap_caps_free(dma_buf);
    heap_caps_free(fb);
}
