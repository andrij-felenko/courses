#include "esp_camera.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

namespace {
constexpr const char *TAG = "camera_loop_cpp";
}

void camera_capture_task_cpp(void *pvParameters)
{
    while (true) {
        camera_fb_t *fb = esp_camera_fb_get();
        if (fb == nullptr) {
            ESP_LOGE(TAG, "Помилка захоплення кадру: буфер порожній");
            vTaskDelay(pdMS_TO_TICKS(100));
            continue;
        }

        ESP_LOGI(TAG, "Отримано кадр: %u байт, %ux%u", 
                 static_cast<unsigned int>(fb->len), fb->width, fb->height);

        // Обов'язкове повернення ресурсу в драйвер
        esp_camera_fb_return(fb);

        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
