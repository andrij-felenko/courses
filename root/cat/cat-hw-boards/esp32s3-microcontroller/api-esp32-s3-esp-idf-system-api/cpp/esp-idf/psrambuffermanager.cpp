#include "esp_heap_caps.h"
#include "esp_log.h"

class PsramBufferManager {
private:
    static constexpr const char *TAG = "PSRAM_CPP";

public:
    static uint8_t *allocateFrameBuffer(size_t width, size_t height) {
        size_t buffer_size = width * height * 2;
        
        void *ptr = heap_caps_malloc(buffer_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
        uint8_t *fb = static_cast<uint8_t *>(ptr);
        
        if (!fb) {
            ESP_LOGE(TAG, "Помилка виділення %zu байтів у PSRAM", buffer_size);
            return nullptr;
        }
        
        ESP_LOGI(TAG, "Виділено буфер PSRAM: %zu байтів", buffer_size);
        return fb;
    }

    static void freeBuffer(uint8_t *fb) {
        if (fb) {
            heap_caps_free(fb);
            ESP_LOGI(TAG, "Звільнено буфер PSRAM");
        }
    }
};
