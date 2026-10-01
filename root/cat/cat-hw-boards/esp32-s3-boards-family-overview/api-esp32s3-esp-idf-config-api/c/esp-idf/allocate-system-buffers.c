#include "esp_heap_caps.h"
#include "esp_log.h"

void allocate_system_buffers(void) {
    // Виділення великого буфера у зовнішній PSRAM
    size_t psram_size = 1024 * 1024; // 1 МБ
    uint8_t *psram_buf = (uint8_t *)heap_caps_malloc(psram_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    
    if (psram_buf == NULL) {
        ESP_LOGE("PSRAM", "Помилка виділення пам'яті у PSRAM!");
        return;
    }
    
    // Виділення DMA-сумісного буфера у внутрішній SRAM
    uint8_t *dma_buf = (uint8_t *)heap_caps_malloc(4096, MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA);
    if (dma_buf != NULL) {
        // Робота з DMA буфером
        heap_caps_free(dma_buf);
    }
    
    heap_caps_free(psram_buf);
}
