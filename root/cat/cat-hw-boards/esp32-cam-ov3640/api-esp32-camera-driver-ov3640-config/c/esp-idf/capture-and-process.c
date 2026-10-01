#include "esp_camera.h"
#include "esp_log.h"

static const char *TAG = "camera_app";

void capture_and_process(void) {
    esp_err_t err = esp_camera_init(&camera_config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації камери: 0x%x", err);
        return;
    }

    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        ESP_LOGE(TAG, "Не вдалося отримати буфер кадру");
        return;
    }

    ESP_LOGI(TAG, "Кадр отримано: %u байт, розмір %ux%u", fb->len, fb->width, fb->height);

    // Обробка кадру або передача даних...

    esp_camera_fb_return(fb);
}
