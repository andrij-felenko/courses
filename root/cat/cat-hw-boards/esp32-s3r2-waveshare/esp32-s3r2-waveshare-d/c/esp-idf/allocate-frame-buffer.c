#include <stdio.h>
#include <stddef.h>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "psram_alloc";

void allocate_frame_buffer(size_t buffer_size) {
    // Виділення ДМА-сумісного буфера у зовнішній Octal PSRAM
    uint8_t *fb = (uint8_t *)heap_caps_malloc(buffer_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_DMA);
    if (fb == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити %d байт у PSRAM", (int)buffer_size);
        return;
    }
    ESP_LOGI(TAG, "Успішно виділено %d байт у SiP PSRAM за адресою %p", (int)buffer_size, fb);
    
    // Звільнення пам'яті після завершення роботи
    heap_caps_free(fb);
}
