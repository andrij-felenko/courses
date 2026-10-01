#include "esp_camera.h"
#include "esp_log.h"

static const char *TAG = "camera_loop";

void capture_task(void *pvParameters) {
    while (1) {
        // Отримання буфера кадру з черги DMA
        camera_fb_t *fb = esp_camera_fb_get();
        if (!fb) {
            ESP_LOGE(TAG, "Помилка захоплення кадру");
            vTaskDelay(pdMS_TO_TICKS(100));
            continue;
        }

        // Обробка даних кадру (наприклад, відправка через HTTP)
        ESP_LOGI(TAG, "Отримано кадр: %u байт, %ux%u", (unsigned int)fb->len, fb->width, fb->height);

        // Обов'язкове повернення буфера назад у кільцевий список DMA
        esp_camera_fb_return(fb);

        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
