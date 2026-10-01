#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "psram_alloc";

void* allocate_frame_buffer(size_t width, size_t height) {
    size_t size = width * height * 2; // RGB565: 2 байти на піксель
    
    // Виділення 16-байтово вирівняної пам'яті в PSRAM з підтримкою DMA
    uint8_t *fb = (uint8_t*)heap_caps_aligned_alloc(16, size, MALLOC_CAP_SPIRAM | MALLOC_CAP_DMA);
    if (!fb) {
        ESP_LOGE(TAG, "Помилка виділення %u байт у PSRAM", (unsigned int)size);
        return NULL;
    }
    
    ESP_LOGI(TAG, "Буфер кадру виділено за адресою %p", fb);
    return fb;
}
