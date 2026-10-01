#include <cstdio>
#include <cstddef>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "heap_example_cpp";

class BufferManager {
public:
    static void allocate_buffers() {
        // Виділення кадрового буфера розміром 1 МБ у зовнішній PSRAM
        const std::size_t psram_size = 1024 * 1024;
        auto *fb = static_cast<uint8_t *>(heap_caps_malloc(psram_size, MALLOC_CAP_SPIRAM));
        if (!fb) {
            ESP_LOGE(TAG, "Помилка виділення PSRAM буфера");
            return;
        }

        // Виділення буфера 4 КБ у внутрішній SRAM з підтримкою DMA
        const std::size_t dma_size = 4096;
        auto *dma_buf = static_cast<uint8_t *>(heap_caps_malloc(dma_size, MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA));
        if (!dma_buf) {
            ESP_LOGE(TAG, "Помилка виділення DMA буфера у SRAM");
            heap_caps_free(fb);
            return;
        }

        ESP_LOGI(TAG, "Буфери успішно виділені у відповідних областях пам'яті");

        heap_caps_free(dma_buf);
        heap_caps_free(fb);
    }
};
