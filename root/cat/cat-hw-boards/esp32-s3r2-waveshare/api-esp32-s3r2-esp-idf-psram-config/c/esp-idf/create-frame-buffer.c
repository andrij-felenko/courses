#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "PSRAM_API";

void create_frame_buffer(size_t width, size_t height) {
    size_t buffer_size = width * height * 2; // RGB565 (2 байти на піксель)
    
    uint16_t *fb = (uint16_t *)heap_caps_malloc(buffer_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    if (fb == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити %d байтів у PSRAM", buffer_size);
        return;
    }
    
    ESP_LOGI(TAG, "Буфер кадру успішно розміщено у PSRAM за адресою %p", fb);
    heap_caps_free(fb);
}
