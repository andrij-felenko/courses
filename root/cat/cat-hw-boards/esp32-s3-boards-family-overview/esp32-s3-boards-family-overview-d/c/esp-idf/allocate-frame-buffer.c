#include <stdio.h>
#include <string.h>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "PSRAM_ALLOC";

void allocate_frame_buffer(void) {
    size_t buffer_size = 640 * 480 * 2; // Буфер під кадр VGA RGB565 (614.4 КБ)
    
    // Виділення пам'яті у зовнішній PSRAM із підтримкою побайтового доступу
    uint8_t *fb = (uint8_t *)heap_caps_malloc(buffer_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    
    if (fb == NULL) {
        ESP_LOGE(TAG, "Помилка виділення пам'яті у PSRAM!");
        return;
    }
    
    ESP_LOGI(TAG, "Успішно виділено %d байт у PSRAM за адресою %p", buffer_size, fb);
    
    // Очищення буфера
    memset(fb, 0, buffer_size);
    
    // Звільнення пам'яті після використання
    heap_caps_free(fb);
}
