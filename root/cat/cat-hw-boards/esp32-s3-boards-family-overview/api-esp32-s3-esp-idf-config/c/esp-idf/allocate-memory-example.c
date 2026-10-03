#include <stdio.h>
#include <string.h>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "HEAP_ALLOC";

void allocate_memory_example(void) {
    size_t buffer_size = 1024 * 128; // 128 КБ
    
    // Виділення великого буфера у зовнішній PSRAM
    uint8_t *psram_buf = (uint8_t *)heap_caps_malloc(buffer_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    if (psram_buf == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити пам'ять у PSRAM!");
        return;
    }
    
    // Виділення вирівняного за кеш-лінією (64 байти) DMA-буфера у внутрішній SRAM
    size_t alignment = 64;
    size_t dma_size = 4096;
    uint8_t *dma_buf = (uint8_t *)heap_caps_aligned_alloc(alignment, dma_size, MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA);
    if (dma_buf == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити DMA-буфер у внутрішній SRAM!");
        heap_caps_free(psram_buf);
        return;
    }

    ESP_LOGI(TAG, "Буфер PSRAM: %p, DMA буфер SRAM: %p", psram_buf, dma_buf);
    
    heap_caps_free(dma_buf);
    heap_caps_free(psram_buf);
}
