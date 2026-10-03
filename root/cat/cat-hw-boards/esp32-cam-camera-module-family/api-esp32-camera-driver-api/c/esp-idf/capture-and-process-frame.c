#include "esp_log.h"
#include "esp_camera.h"

static const char *TAG = "camera_main";

esp_err_t capture_and_process_frame(void) {
    // 1. Запит кадрового буфера з драйвера
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        ESP_LOGE(TAG, "Помилка захоплення кадру: буфер порожній");
        return ESP_FAIL;
    }

    // 2. Обробка кадру (наприклад, вивід розміру)
    ESP_LOGI(TAG, "Отримано кадр розміром %d байтів, %dx%d", 
             (int)fb->len, fb->width, fb->height);

    // 3. Обов'язкове повернення буфера драйверу
    esp_camera_fb_return(fb);
    return ESP_OK;
}
