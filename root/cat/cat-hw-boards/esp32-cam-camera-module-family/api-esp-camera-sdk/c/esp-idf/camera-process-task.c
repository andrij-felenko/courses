#include "esp_camera.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "frame_loop";

void camera_process_task(void *pvParameters) {
    while (1) {
        // 1. Отримання кадрового буфера з черги DMA
        camera_fb_t *fb = esp_camera_fb_get();
        if (!fb) {
            ESP_LOGE(TAG, "Не вдалося отримати кадр з камери");
            vTaskDelay(pdMS_TO_TICKS(100));
            continue;
        }

        // 2. Обробка кадру (наприклад, друк розміру буфера)
        ESP_LOGI(TAG, "Кадр отримано: %ux%u, розмір: %u байтів", 
                 (unsigned int)fb->width, (unsigned int)fb->height, (unsigned int)fb->len);

        // 3. Обов'язкове повернення кадрового буфера в пул драйвера
        esp_camera_fb_return(fb);
        fb = NULL; // Запобігання повторному використанню вказівника

        vTaskDelay(pdMS_TO_TICKS(33)); // ~30 кадрів за секунду
    }
}
