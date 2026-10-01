#include <stdio.h>
#include <string.h>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "PSRAM_DEMO";

void allocate_framebuffer(void)
{
    // Розмір кадрового буфера SVGA RGB565 (800 x 600 x 2 байти)
    size_t fb_size = 800 * 600 * 2;

    // Запит виділення пам'яті у зовнішній PSRAM із підтримкою 8-бітного доступу
    uint8_t *frame_buffer = (uint8_t *)heap_caps_malloc(fb_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);

    if (frame_buffer == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити %d байтів у PSRAM!", (int)fb_size);
        return;
    }

    ESP_LOGI(TAG, "Успішно виділено кадровий буфер за адресою: %p", frame_buffer);

    // Ініціалізація буфера тестовим значенням
    memset(frame_buffer, 0xAA, fb_size);

    // Очищення та звільнення ресурсів після використання
    heap_caps_free(frame_buffer);
    ESP_LOGI(TAG, "Буфер у PSRAM успішно звільнено");
}
