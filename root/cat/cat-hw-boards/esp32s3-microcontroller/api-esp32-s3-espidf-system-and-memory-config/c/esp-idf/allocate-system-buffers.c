#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "MEM_CFG";

void allocate_system_buffers(void) {
    // Виділення 1 МБ у зовнішній PSRAM під буфер кадрів
    uint8_t *frame_buffer = (uint8_t *)heap_caps_malloc(1024 * 1024, MALLOC_CAP_SPIRAM);
    if (frame_buffer == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити пам'ять у PSRAM!");
    }

    // Виділення 4 КБ у внутрішній SRAM з підтримкою DMA для шини SPI
    uint8_t *dma_buffer = (uint8_t *)heap_caps_malloc(4096, MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA);
    if (dma_buffer == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити DMA-буфер у внутрішній пам'яті!");
    }
}
