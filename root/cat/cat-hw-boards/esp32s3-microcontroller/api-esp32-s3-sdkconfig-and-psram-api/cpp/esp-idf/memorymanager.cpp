#include <cstdio>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "MEM_ALLOC_CPP";

class MemoryManager {
public:
    static void AllocateBuffers() {
        // Виділення великого кадрового буфера у зовнішній PSRAM
        std::size_t frame_buffer_size = 640 * 480 * 2;
        auto *frame_buffer = static_cast<uint16_t *>(heap_caps_malloc(frame_buffer_size, MALLOC_CAP_SPIRAM));
        if (!frame_buffer) {
            ESP_LOGE(TAG, "Помилка виділення PSRAM");
        } else {
            ESP_LOGI(TAG, "Буфер у PSRAM: %p", frame_buffer);
        }

        // Виділення DMA-сумісного буфера у внутрішній SRAM
        std::size_t dma_buffer_size = 4096;
        auto *dma_buffer = static_cast<uint8_t *>(heap_caps_malloc(dma_buffer_size, MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA));
        if (!dma_buffer) {
            ESP_LOGE(TAG, "Помилка виділення DMA SRAM");
        } else {
            ESP_LOGI(TAG, "DMA буфер: %p", dma_buffer);
        }

        heap_caps_free(frame_buffer);
        heap_caps_free(dma_buffer);
    }
};
