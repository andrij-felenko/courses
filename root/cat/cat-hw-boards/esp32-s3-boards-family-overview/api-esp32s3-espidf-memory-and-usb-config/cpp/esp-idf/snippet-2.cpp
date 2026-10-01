#include <cstdio>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "MAIN_CPP";

extern "C" void app_main(void)
{
    constexpr size_t buffer_size = 512 * 1024; // 512 КБайт

    // Виділення масиву об'єктів у зовнішній PSRAM
    uint8_t *psram_buffer = static_cast<uint8_t *>(heap_caps_malloc(buffer_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
    if (!psram_buffer) {
        ESP_LOGE(TAG, "Помилка виділення буфера у PSRAM!");
    } else {
        ESP_LOGI(TAG, "Буфер у PSRAM успішно створено");
    }

    // Виділення швидкого внутрішнього буфера SRAM під DMA
    uint8_t *sram_dma_buffer = static_cast<uint8_t *>(heap_caps_malloc(4096, MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA));
    if (!sram_dma_buffer) {
        ESP_LOGE(TAG, "Помилка виділення DMA буфера");
    } else {
        ESP_LOGI(TAG, "DMA буфер успішно виділено у внутрішній SRAM");
    }

    heap_caps_free(psram_buffer);
    heap_caps_free(sram_dma_buffer);
}
