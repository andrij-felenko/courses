#include <cstddef>
#include <cstdint>
#include "esp_heap_caps.h"
#include "esp_log.h"

class FrameBufferManager {
private:
    static constexpr const char *TAG = "BufferManager";
    static constexpr size_t CACHE_LINE_SIZE = 64;

public:
    static uint8_t* createAlignedBuffer(size_t width, size_t height, size_t bpp) {
        size_t totalBytes = width * height * bpp;
        
        // Виділення пам'яті в зовнішній PSRAM з вирівнюванням по кеш-лінії
        void* ptr = heap_caps_aligned_alloc(CACHE_LINE_SIZE, totalBytes, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
        
        if (!ptr) {
            ESP_LOGE(TAG, "Не вдалося виділити %zu байтів у PSRAM", totalBytes);
            return nullptr;
        }
        
        ESP_LOGI(TAG, "Створено вирівняний буфер за адресою: %p", ptr);
        return static_cast<uint8_t*>(ptr);
    }

    static void freeBuffer(uint8_t* buffer) {
        if (buffer) {
            heap_caps_free(buffer);
        }
    }
};
