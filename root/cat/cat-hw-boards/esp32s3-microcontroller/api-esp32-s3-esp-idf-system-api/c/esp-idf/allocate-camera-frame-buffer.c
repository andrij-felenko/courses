#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "PSRAM_ALLOC";

// Виділення кадрового буфера у зовнішній PSRAM
uint8_t *allocate_camera_frame_buffer(size_t width, size_t height) {
    size_t buffer_size = width * height * 2; // 2 байти на піксель для RGB565
    
    // Виділення пам'яті у PSRAM з атрибутом побайтового доступу
    uint8_t *fb = (uint8_t *)heap_caps_malloc(buffer_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    
    if (fb == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити %zu байтів у PSRAM!", buffer_size);
        return NULL;
    }
    
    ESP_LOGI(TAG, "Успішно виділено %zu байтів кадрового буфера за адресою %p", buffer_size, (void *)fb);
    return fb;
}

void free_camera_frame_buffer(uint8_t *fb) {
    if (fb != NULL) {
        heap_caps_free(fb);
        ESP_LOGI(TAG, "Буфер у PSRAM успішно звільнено");
    }
}
