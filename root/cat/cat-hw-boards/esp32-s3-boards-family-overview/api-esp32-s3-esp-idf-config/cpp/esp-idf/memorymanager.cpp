#include <cstdint>
#include <cstddef>
#include "esp_heap_caps.h"
#include "esp_log.h"

class MemoryManager {
private:
    static constexpr const char *TAG = "HEAP_ALLOC";
public:
    static void allocate() {
        size_t buffer_size = 1024 * 128;
        uint8_t *psram_buf = static_cast<uint8_t*>(heap_caps_malloc(buffer_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
        if (!psram_buf) {
            ESP_LOGE(TAG, "Помилка виділення у PSRAM");
            return;
        }

        size_t alignment = 64;
        size_t dma_size = 4096;
        uint8_t *dma_buf = static_cast<uint8_t*>(heap_caps_aligned_alloc(alignment, dma_size, MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA));
        if (!dma_buf) {
            ESP_LOGE(TAG, "Помилка виділення DMA буфера");
            heap_caps_free(psram_buf);
            return;
        }

        ESP_LOGI(TAG, "Буфер PSRAM: %p, DMA буфер: %p", psram_buf, dma_buf);

        heap_caps_free(dma_buf);
        heap_caps_free(psram_buf);
    }
};
