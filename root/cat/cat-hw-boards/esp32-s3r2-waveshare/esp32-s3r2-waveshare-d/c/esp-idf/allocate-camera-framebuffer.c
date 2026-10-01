#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "PSRAM_BUF";

uint8_t *allocate_camera_framebuffer(size_t width, size_t height) {
    size_t buffer_size = width * height * 2; // RGB565 (2 байти на піксель)
    
    // Виділення кадрового буфера у зовнішній пам'яті PSRAM із вирівнюванням
    uint8_t *fb = (uint8_t *)heap_caps_malloc(buffer_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    
    if (fb == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити %d байтів у PSRAM!", buffer_size);
        return NULL;
    }
    
    ESP_LOGI(TAG, "Успішно виділено %d байтів у PSRAM за адресою %p", buffer_size, fb);
    return fb;
}
