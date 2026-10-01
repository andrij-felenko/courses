#include <stdio.h>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "PSRAM_ALLOC";

void allocate_psram_buffer(size_t buffer_size) {
    // Виділення очищеного нулями масиву в PSRAM з підтримкою 8-бітного доступу
    uint8_t *fb = (uint8_t *)heap_caps_calloc(1, buffer_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    
    if (fb == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити %d байтів у PSRAM!", buffer_size);
        return;
    }
    
    ESP_LOGI(TAG, "Успішно виділено %d байтів у PSRAM за адресою %p", buffer_size, (void *)fb);
    
    // Звільнення виділеної пам'яті
    heap_caps_free(fb);
}
