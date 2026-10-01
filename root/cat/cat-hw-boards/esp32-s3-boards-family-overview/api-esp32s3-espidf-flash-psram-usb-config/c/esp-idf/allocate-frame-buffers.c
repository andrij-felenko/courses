#include <stdio.h>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "mem_app";

void allocate_frame_buffers(void) {
    // Виділення великого кадрового буфера у зовнішній PSRAM
    size_t buffer_size = 1024 * 768; // 768 КБ
    uint8_t *psram_buffer = (uint8_t *)heap_caps_malloc(buffer_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    
    if (psram_buffer == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити пам'ять у PSRAM!");
        return;
    }
    ESP_LOGI(TAG, "Буфер у PSRAM успішно виділено за адресою: %p", psram_buffer);

    // Виділення критичного DMA-буфера у внутрішній пам'яті SRAM
    uint8_t *dma_buffer = (uint8_t *)heap_caps_malloc(1024, MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA);
    if (dma_buffer != NULL) {
        ESP_LOGI(TAG, "DMA буфер у внутрішній SRAM виділено за адресою: %p", dma_buffer);
        heap_caps_free(dma_buffer);
    }

    heap_caps_free(psram_buffer);
}
