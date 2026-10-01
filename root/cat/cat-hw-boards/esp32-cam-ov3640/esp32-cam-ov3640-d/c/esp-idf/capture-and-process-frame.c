#include "esp_camera.h"
#include "esp_log.h"

static const char *TAG = "camera_example";

void capture_and_process_frame(void)
{
    // Отримання кадрового буфера з PSRAM
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        ESP_LOGE(TAG, "Помилка захоплення кадру з камери");
        return;
    }

    ESP_LOGI(TAG, "Отримано кадр: розмір %u байт, ширина %u, висота %u",
             (unsigned int)fb->len, (unsigned int)fb->width, (unsigned int)fb->height);

    // Обов'язкове повернення буфера у пул драйвера для запобігання витокам PSRAM
    esp_camera_fb_return(fb);
}
