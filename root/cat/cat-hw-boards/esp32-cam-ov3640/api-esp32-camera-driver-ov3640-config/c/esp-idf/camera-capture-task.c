#include "esp_camera.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "camera_loop";

void camera_capture_task(void *pvParameters)
{
    while (1) {
        camera_fb_t *fb = esp_camera_fb_get();
        if (!fb) {
            ESP_LOGE(TAG, "Не вдалося отримати кадр з камери");
            vTaskDelay(pdMS_TO_TICKS(100));
            continue;
        }

        // Обробка кадру (наприклад, передача даних через HTTP/Wi-Fi)
        ESP_LOGI(TAG, "Кадр отримано: %u байт, розмір %ux%u", 
                 (unsigned int)fb->len, fb->width, fb->height);

        // Обов'язкове вивільнення кадрового буфера назад у DMA-кільце
        esp_camera_fb_return(fb);
        
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
