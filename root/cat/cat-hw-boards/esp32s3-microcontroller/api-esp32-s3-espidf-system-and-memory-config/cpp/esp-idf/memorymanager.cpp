#include "esp_heap_caps.h"
#include "esp_log.h"
#include <cstdint>

class MemoryManager {
private:
    static constexpr const char* TAG = "MEM_CFG";

public:
    uint8_t* allocateSpiramBuffer(size_t size) {
        uint8_t* ptr = static_cast<uint8_t*>(heap_caps_malloc(size, MALLOC_CAP_SPIRAM));
        if (!ptr) {
            ESP_LOGE(TAG, "Помилка виділення %z байти у PSRAM", size);
        }
        return ptr;
    }

    uint8_t* allocateDmaBuffer(size_t size) {
        uint8_t* ptr = static_cast<uint8_t*>(heap_caps_malloc(size, MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA));
        if (!ptr) {
            ESP_LOGE(TAG, "Помилка виділення DMA буфера %z байти", size);
        }
        return ptr;
    }
};
