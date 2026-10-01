#include <stdio.h>
#include <stddef.h>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "PSRAM_ALLOC";

void allocate_framebuffer(void)
{
    size_t fb_size = 320 * 240 * 2; // 153.6 КБ для дисплея RGB565

    // Виділення кадрового буфера у зовнішній PSRAM
    uint16_t *framebuffer = (uint16_t *)heap_caps_malloc(fb_size, MALLOC_CAP_SPIRAM);

    if (framebuffer == NULL) {
        ESP_LOGE(TAG, "Помилка виділення кадрового буфера у PSRAM!");
        return;
    }

    ESP_LOGI(TAG, "Кадровий буфер %d байт успішно виділено у PSRAM за адресою %p", 
             (int)fb_size, (void *)framebuffer);

    // Звільнення пам'яті після використання
    heap_caps_free(framebuffer);
}
