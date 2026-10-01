#include "esp_log.h"
#include "esp_camera.h"

static const char *TAG = "camera_app";

void capture_and_process(void) {
    esp_err_t err = esp_camera_init(&camera_config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації камери: 0x%x", err);
        return;
    }

    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        ESP_LOGE(TAG, "Не вдалося отримати кадр");
        return;
    }

    ESP_LOGI(TAG, "Отримано кадр: %zu байт, розмір %ux%u", fb->len, fb->width, fb->height);

    // Звільнення буфера пам'яті назад до драйвера
    esp_camera_fb_return(fb);
}
