#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "mem_api";

void allocate_memory_example(void) {
    size_t free_psram = heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
    ESP_LOGI(TAG, "Доступно PSRAM: %u байтів", free_psram);

    // Виділення кадрового буфера у зовнішній PSRAM
    uint8_t *frame_buffer = (uint8_t *)heap_caps_malloc(1024 * 1024, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    if (frame_buffer == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити буфер у PSRAM!");
        return;
    }

    // Виділення критичного буфера у внутрішній SRAM
    uint32_t *dma_buffer = (uint32_t *)heap_caps_malloc(512 * sizeof(uint32_t), MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA);
    if (dma_buffer == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити DMA буфер у SRAM!");
        heap_caps_free(frame_buffer);
        return;
    }

    // Звільнення виділеної пам'яті
    heap_caps_free(frame_buffer);
    heap_caps_free(dma_buffer);
}
