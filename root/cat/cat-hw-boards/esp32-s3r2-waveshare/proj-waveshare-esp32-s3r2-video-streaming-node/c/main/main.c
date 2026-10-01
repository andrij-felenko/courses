#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_system.h"
#include "esp_heap_caps.h"
#include "camera_psram_config.h"

static const char *TAG = "MAIN_APP";

void app_main(void)
{
    ESP_LOGI(TAG, "Старт системи Waveshare ESP32-S3R2");

    // Виведення діагностики внутрішньої SRAM та зовнішньої Octal PSRAM
    size_t internal_free = heap_caps_get_free_size(MALLOC_CAP_INTERNAL);
    size_t psram_free = heap_caps_get_free_size(MALLOC_CAP_SPIRAM);

    ESP_LOGI(TAG, "Діагностика адресної сітки купи:");
    ESP_LOGI(TAG, "  Внутрішня SRAM (DMA-capable): %u байт", internal_free);
    ESP_LOGI(TAG, "  Зовнішня Octal PSRAM:          %u байт", psram_free);

    // Ініціалізація конфігурації камери
    camera_config_t camera_config;
    bool camera_in_psram = false;

    esp_err_t err = configure_camera_for_psram(&camera_config, &camera_in_psram);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка формування конфігурації камери: 0x%x", err);
        return;
    }

    // Ініціалізація драйвера камери
    ESP_LOGI(TAG, "Ініціалізація драйвера esp_camera_init()...");
    err = esp_camera_init(&camera_config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Сбій ініціалізації камери (код помилки 0x%x)", err);
        ESP_LOGE(TAG, "Перевірте підключення сенсора та ліній D0-D7/PCLK");
        return;
    }

    ESP_LOGI(TAG, "Камеру успішно ініціалізовано. Буфери у %s", 
             camera_in_psram ? "Octal PSRAM" : "Внутрішній SRAM");

    // Тестовий цикл захоплення кадрів та моніторингу залишку пам'яті
    for (int i = 1; i <= 3; i++) {
        vTaskDelay(pdMS_TO_TICKS(1000));

        ESP_LOGI(TAG, "Спроба захоплення кадру #%d...", i);
        camera_fb_t *fb = esp_camera_fb_get();

        if (!fb) {
            ESP_LOGE(TAG, "Помилка захоплення кадру #%d", i);
            continue;
        }

        ESP_LOGI(TAG, "Кадр #%d отримано: розмір=%u байт, ширина=%u, висота=%u, формат=%d",
                 i, fb->len, fb->width, fb->height, fb->format);

        // Повернення кадрового буфера драйверу
        esp_camera_fb_return(fb);

        // Моніторинг залишку псевдостатичної пам'яті після захоплення
        size_t current_psram = heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
        ESP_LOGI(TAG, "Поточний залишок PSRAM: %u байт", current_psram);
    }

    ESP_LOGI(TAG, "Тестування кадрових буферів завершено успішно.");
}
