#include <iostream>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "PSRAM_ALLOC_CPP";

class FrameBuffer {
public:
    uint8_t *data;
    size_t size;

    FrameBuffer(size_t width, size_t height, size_t bpp) : data(nullptr), size(width * height * bpp) {
        // Запит пам'яті у зовнішній PSRAM через системний API ESP-IDF
        data = static_cast<uint8_t*>(heap_caps_malloc(size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
        if (!data) {
            ESP_LOGW(TAG, "Резервне виділення кадрового буфера у внутрішній SRAM");
            data = static_cast<uint8_t*>(heap_caps_malloc(size, MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT));
        }
    }

    ~FrameBuffer() {
        if (data) {
            heap_caps_free(data);
        }
    }
};
