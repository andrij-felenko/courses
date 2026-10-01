#include "esp_heap_caps.h"
#include "esp_log.h"
#include <cstdint>

class MemoryManager {
private:
    static constexpr const char *TAG = "MemMgr";

public:
    static void allocateBuffers() {
        // Виділення кадрового буфера 1 МБ у зовнішній PSRAM
        auto *fb = static_cast<uint8_t *>(heap_caps_malloc(1024 * 1024, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
        if (!fb) {
            ESP_LOGE(TAG, "Помилка виділення буфера в PSRAM");
            return;
        }

        // Виділення буфера DMA 4 КБ у внутрішній SRAM
        auto *dma_buf = static_cast<uint8_t *>(heap_caps_malloc(4096, MALLOC_CAP_DMA | MALLOC_CAP_INTERNAL));
        if (!dma_buf) {
            ESP_LOGE(TAG, "Помилка виділення DMA буфера в SRAM");
            heap_caps_free(fb);
            return;
        }

        heap_caps_free(dma_buf);
        heap_caps_free(fb);
    }
};
