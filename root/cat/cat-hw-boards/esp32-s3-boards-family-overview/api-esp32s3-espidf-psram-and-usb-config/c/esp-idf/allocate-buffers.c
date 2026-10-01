#include <stdio.h>
#include <stddef.h>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "heap_example";

void allocate_buffers(void) {
    // Виділення кадрового буфера розміром 1 МБ у зовнішній PSRAM
    size_t psram_size = 1024 * 1024;
    uint8_t *fb = (uint8_t *)heap_caps_malloc(psram_size, MALLOC_CAP_SPIRAM);
    if (fb == NULL) {
        ESP_LOGE(TAG, "Помилка виділення PSRAM буфера");
        return;
    }

    // Виділення буфера 4 КБ у внутрішній SRAM з підтримкою DMA
    size_t dma_size = 4096;
    uint8_t *dma_buf = (uint8_t *)heap_caps_malloc(dma_size, MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA);
    if (dma_buf == NULL) {
        ESP_LOGE(TAG, "Помилка виділення DMA буфера у SRAM");
        heap_caps_free(fb);
        return;
    }

    ESP_LOGI(TAG, "Буфери успішно виділені у відповідних областях пам'яті");

    // Звільнення ресурсів
    heap_caps_free(dma_buf);
    heap_caps_free(fb);
}
