#include <stdio.h>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "psram_alloc";

void allocate_frame_buffer(size_t width, size_t height) {
    size_t buffer_size = width * height * 2; // RGB565: 2 байти на піксель
    
    // Виділення буфера кадрового масиву в зовнішній PSRAM
    uint8_t *fb = (uint8_t *)heap_caps_malloc(
        buffer_size, 
        MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT
    );
    
    if (fb == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити %zu байтів у PSRAM!", buffer_size);
        return;
    }
    
    ESP_LOGI(TAG, "Успішно виділено %zu байтів у PSRAM за адресою %p", buffer_size, (void *)fb);
    
    // Звільнення виділеної пам'яті
    heap_caps_free(fb);
}
