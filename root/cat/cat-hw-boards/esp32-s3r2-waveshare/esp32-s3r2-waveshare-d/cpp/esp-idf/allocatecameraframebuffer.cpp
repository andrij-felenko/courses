#include "esp_heap_caps.h"
#include "esp_log.h"
#include <cstddef>

static const char *TAG = "PSRAM_BUF";

uint8_t *allocateCameraFramebuffer(std::size_t width, std::size_t height) {
    std::size_t bufferSize = width * height * 2; // RGB565 (2 байти на піксель)
    
    // Виділення кадрового буфера у зовнішній пам'яті PSRAM із вирівнюванням
    uint8_t *fb = static_cast<uint8_t *>(heap_caps_malloc(bufferSize, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
    
    if (fb == nullptr) {
        ESP_LOGE(TAG, "Не вдалося виділити %d байтів у PSRAM!", bufferSize);
        return nullptr;
    }
    
    ESP_LOGI(TAG, "Успішно виділено %d байтів у PSRAM за адресою %p", bufferSize, fb);
    return fb;
}
