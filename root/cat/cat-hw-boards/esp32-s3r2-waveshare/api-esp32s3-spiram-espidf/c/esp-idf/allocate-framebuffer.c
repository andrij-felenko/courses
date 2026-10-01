#include <stdio.h>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "PSRAM_ALLOC";

void allocate_framebuffer(size_t width, size_t height) {
    size_t buffer_size = width * height * 2; // 16-бітний колір

    // Виділення буфера кадру безпосередньо у PSRAM
    uint8_t *fb = (uint8_t *)heap_caps_malloc(buffer_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);

    if (fb == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити %zu байт у PSRAM!", buffer_size);
        return;
    }

    ESP_LOGI(TAG, "Успішно виділено буфер кадру за адресою %p", fb);

    // Робота з буфером...
    fb[0] = 0xFF;

    // Звільнення пам'яті через спеціалізовану або стандартну функцію
    heap_caps_free(fb);
}
