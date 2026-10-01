#include <stdio.h>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "PSRAM_API";

void allocate_buffers(void) {
    size_t psram_size = 512 * 1024; // 512 кБ під графічний буфер
    uint8_t *fb = (uint8_t *)heap_caps_malloc(psram_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    
    if (fb == NULL) {
        ESP_LOGE(TAG, "Помилка виділення кадрового буфера у PSRAM!");
        return;
    }
    ESP_LOGI(TAG, "Кадровий буфер 512 кБ успішно виділено у PSRAM");

    size_t dma_size = 4 * 1024; // 4 кБ під DMA буфер
    uint8_t *dma_buf = (uint8_t *)heap_caps_malloc(dma_size, MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA);
    
    if (dma_buf == NULL) {
        ESP_LOGE(TAG, "Помилка виділення DMA буфера у SRAM!");
        heap_caps_free(fb);
        return;
    }
    ESP_LOGI(TAG, "DMA буфер 4 кБ виділено у внутрішній SRAM");

    // Звільнення ресурсів
    heap_caps_free(dma_buf);
    heap_caps_free(fb);
}
