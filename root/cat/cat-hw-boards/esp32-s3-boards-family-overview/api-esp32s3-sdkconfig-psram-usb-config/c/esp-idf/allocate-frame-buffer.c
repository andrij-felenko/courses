#include <stdio.h>
#include <string.h>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "PSRAM_ALLOC";

void allocate_frame_buffer(void) {
    size_t buffer_size = 1024 * 1024; // 1 МБ для кадрового буфера

    // Виділення пам'яті у зовнішній PSRAM
    uint8_t *fb = (uint8_t *)heap_caps_malloc(buffer_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);

    if (fb == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити %d байтів у PSRAM!", buffer_size);
        return;
    }

    memset(fb, 0, buffer_size);
    ESP_LOGI(TAG, "Успішно виділено %d байтів у PSRAM за адресою: %p", buffer_size, (void *)fb);

    // Звільнення пам'яті після використання
    heap_caps_free(fb);
}
