#include "esp_system.h"
#include "esp_heap_caps.h"
#include "esp_log.h"

class SystemMemoryManager {
private:
    static constexpr const char *TAG = "MemoryManager";

public:
    static void printMemoryStatus() {
        size_t psramSize = heap_caps_get_total_size(MALLOC_CAP_SPIRAM);
        ESP_LOGI(TAG, "Загальний обсяг PSRAM: %d байт", psramSize);
    }

    static uint8_t* allocateFrameBuffer(size_t width, size_t height) {
        uint8_t *buffer = static_cast<uint8_t*>(heap_caps_malloc(width * height, MALLOC_CAP_SPIRAM));
        if (!buffer) {
            ESP_LOGE(TAG, "Помилка виділення буфера у PSRAM");
        }
        return buffer;
    }
};

extern "C" void app_main(void) {
    SystemMemoryManager::printMemoryStatus();
    uint8_t *fb = SystemMemoryManager::allocateFrameBuffer(640, 480);
    if (fb) {
        heap_caps_free(fb);
    }
}
