#include <cstdio>
#include "esp_heap_caps.h"
#include "esp_log.h"

constexpr const char *TAG = "PSRAM_API_CPP";

class MemoryManager {
public:
    static bool allocate_system_buffers(uint8_t *&psram_buf, uint8_t *&dma_buf, size_t psram_bytes, size_t dma_bytes) {
        psram_buf = static_cast<uint8_t*>(heap_caps_malloc(psram_bytes, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
        if (!psram_buf) {
            ESP_LOGE(TAG, "Не вдалося виділити PSRAM буфер");
            return false;
        }

        dma_buf = static_cast<uint8_t*>(heap_caps_malloc(dma_bytes, MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA));
        if (!dma_buf) {
            ESP_LOGE(TAG, "Не вдалося виділити DMA буфер");
            heap_caps_free(psram_buf);
            psram_buf = nullptr;
            return false;
        }

        return true;
    }

    static void free_buffers(uint8_t *psram_buf, uint8_t *dma_buf) {
        if (dma_buf) heap_caps_free(dma_buf);
        if (psram_buf) heap_caps_free(psram_buf);
    }
};
