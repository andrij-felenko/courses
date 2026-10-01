#include <cstdio>
#include <cstddef>
#include <cstdint>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "PSRAM_ALLOC_CPP";

class FramebufferManager {
public:
    static uint16_t* allocate(size_t width, size_t height) {
        size_t bytes = width * height * sizeof(uint16_t);
        auto *ptr = static_cast<uint16_t*>(heap_caps_malloc(bytes, MALLOC_CAP_SPIRAM));
        
        if (!ptr) {
            ESP_LOGE(TAG, "Не вдалося виділити %zu байт у PSRAM", bytes);
        } else {
            ESP_LOGI(TAG, "Виділено %zu байт у PSRAM", bytes);
        }
        return ptr;
    }

    static void free_buffer(uint16_t *ptr) {
        if (ptr) {
            heap_caps_free(ptr);
        }
    }
};
