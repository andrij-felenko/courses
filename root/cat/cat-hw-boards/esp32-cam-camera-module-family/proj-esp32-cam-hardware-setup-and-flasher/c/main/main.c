#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_psram.h"
#include "esp_camera.h"

static const char *TAG = "main";

// Декларація функції ініціалізації камери з camera_init.c
esp_err_t init_camera(void);

void app_main(void)
{
    ESP_LOGI(TAG, "Запуск модуля ESP32-CAM...");

    // Перевірка стану оперативної пам'яті PSRAM
    if (esp_psram_is_initialized()) {
        size_t psram_size = esp_psram_get_size();
        ESP_LOGI(TAG, "PSRAM ініціалізовано успішно. Обсяг: %u байт.", psram_size);
    } else {
        ESP_LOGW(TAG, "Увага: Зовнішня PSRAM відсутня або не активована.");
    }

    // Ініціалізація камери
    if (init_camera() != ESP_OK) {
        ESP_LOGE(TAG, "Критична помилка: Не вдалося ініціалізувати камеру. Роботу зупинено.");
        return;
    }

    ESP_LOGI(TAG, "Камера готова. Початок циклу захоплення кадрів...");

    // Демонстраційний цикл вибірки та звільнення кадрових буферів
    for (int i = 0; i < 5; i++) {
        ESP_LOGI(TAG, "Отримання кадру #%d...", i + 1);

        // Захоплення кадрового буфера
        camera_fb_t *fb = esp_camera_fb_get();
        if (!fb) {
            ESP_LOGE(TAG, "Помилка захоплення кадру #%d", i + 1);
            vTaskDelay(pdMS_TO_TICKS(1000));
            continue;
        }

        // Обробка інформації про кадр
        ESP_LOGI(TAG, "Кадр #%d успішно отримано! Формат: %d, Розмір: %u байт, Ширина: %d, Висота: %d",
                 i + 1, fb->format, fb->len, fb->width, fb->height);

        // Обов'язкове повернення кадрового буфера в систему для запобігання витокам пам'яті
        esp_camera_fb_return(fb);
        fb = NULL;

        vTaskDelay(pdMS_TO_TICKS(2000));
    }

    ESP_LOGI(TAG, "Демонстраційний цикл захоплення кадрів завершено.");
}
