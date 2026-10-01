#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_psram.h"
#include "psram_framebuffer.h"

static const char *TAG = "MAIN";

// Задача малювання кадрів у фоновому буфері PSRAM
static void render_task(void *pvParameters)
{
    psram_fb_t *fb = (psram_fb_t *)pvParameters;
    uint16_t color_counter = 0;

    while (1) {
        // Отримуємо вказівник на робочий буфер (back buffer)
        uint16_t *pixel_ptr = (uint16_t *)fb->back_buffer;

        // Заповнюємо кадровий буфер кольоровим градієнтом
        for (int y = 0; y < FB_HEIGHT; y++) {
            for (int x = 0; x < FB_WIDTH; x++) {
                uint16_t r = (x + color_counter) & 0x1F;
                uint16_t g = (y + color_counter) & 0x3F;
                uint16_t b = (x + y) & 0x1F;
                pixel_ptr[y * FB_WIDTH + x] = (r << 11) | (g << 5) | b;
            }
        }
        color_counter++;

        // Скидаємо кеш пам'яті для узгодженості даних PSRAM з DMA
        psram_fb_flush_cache(fb);

        // Безпечно перемикаємо буфери
        psram_fb_swap(fb);

        // Імітуємо частоту оновлення екрана ~30 FPS
        vTaskDelay(pdMS_TO_TICKS(33));
    }
}

void app_main(void)
{
    ESP_LOGI(TAG, "Запуск проєкту подвійної кадрової буферизації Waveshare ESP32-S3R2");

    // Перевіряємо наявність та доступність зовнішньої пам'яті PSRAM
    if (!esp_psram_is_initialized()) {
        ESP_LOGE(TAG, "Помилка: Зовнішня пам'ять PSRAM не ініціалізована!");
        return;
    }

    size_t psram_size = heap_caps_get_total_size(MALLOC_CAP_SPIRAM);
    ESP_LOGI(TAG, "Доступний обсяг PSRAM: %d КБ", psram_size / 1024);

    static psram_fb_t fb;

    // Ініціалізуємо подвійний кадровий буфер у PSRAM
    esp_err_t ret = psram_fb_init(&fb, FB_WIDTH, FB_HEIGHT);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації кадрового буфера!");
        return;
    }

    // Запускаємо задачу відмалювання кадрів на другому ядрі ЦПУ
    xTaskCreatePinnedToCore(
        render_task,
        "render_task",
        4096,
        &fb,
        5,
        NULL,
        1
    );

    ESP_LOGI(TAG, "Задачу рендерингу успішно запущено на Core 1");
}
