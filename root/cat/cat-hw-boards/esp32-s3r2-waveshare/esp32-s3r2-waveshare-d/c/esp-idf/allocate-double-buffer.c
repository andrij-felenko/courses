#include <stdio.h>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "PSRAM_ALLOC";

void allocate_double_buffer(size_t buffer_size) {
    // Виділення двох кадрових буферів у псевдостатичній пам'яті PSRAM
    uint8_t *fb1 = (uint8_t *)heap_caps_malloc(buffer_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    uint8_t *fb2 = (uint8_t *)heap_caps_malloc(buffer_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);

    if (fb1 == NULL || fb2 == NULL) {
        ESP_LOGE(TAG, "Помилка виділення пам'яті у PSRAM");
        if (fb1) heap_caps_free(fb1);
        if (fb2) heap_caps_free(fb2);
        return;
    }

    ESP_LOGI(TAG, "Успішно виділено %d байтів у PSRAM", buffer_size * 2);

    // Використання буферів...

    heap_caps_free(fb1);
    heap_caps_free(fb2);
}
