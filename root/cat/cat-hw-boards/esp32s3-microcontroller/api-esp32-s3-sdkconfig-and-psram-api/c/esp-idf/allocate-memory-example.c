#include <stdio.h>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "MEM_ALLOC";

void allocate_memory_example(void)
{
    // Виділення великого кадрового буфера 640x480 RGB565 (614.4 КБ) у зовнішній PSRAM
    size_t frame_buffer_size = 640 * 480 * 2;
    uint16_t *frame_buffer = (uint16_t *)heap_caps_malloc(frame_buffer_size, MALLOC_CAP_SPIRAM);
    if (frame_buffer == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити кадровій буфер у PSRAM");
    } else {
        ESP_LOGI(TAG, "Кадровий буфер у PSRAM успішно виділено: %p", frame_buffer);
    }

    // Виділення 4 КБ DMA-буфера у внутрішній SRAM для передачі по SPI
    size_t dma_buffer_size = 4096;
    uint8_t *dma_buffer = (uint8_t *)heap_caps_malloc(dma_buffer_size, MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA);
    if (dma_buffer == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити DMA-буфер у внутрішній SRAM");
    } else {
        ESP_LOGI(TAG, "DMA-буфер у внутрішній SRAM успішно виділено: %p", dma_buffer);
    }

    // Звільнення виділеної пам'яті
    heap_caps_free(frame_buffer);
    heap_caps_free(dma_buffer);
}
