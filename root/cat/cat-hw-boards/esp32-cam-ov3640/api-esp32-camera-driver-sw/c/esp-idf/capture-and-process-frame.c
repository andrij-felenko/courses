// Безпечний цикл захоплення та обробки кадрів в ESP-IDF
#include "esp_camera.h"
#include "esp_log.h"

void capture_and_process_frame(void) {
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        ESP_LOGE("CAM", "Не вдалося отримати кадр з камери");
        return;
    }

    // Обробка даних кадру (наприклад, перевірка розміру буфера)
    ESP_LOGI("CAM", "Захоплено кадр: %d x %d, розмір: %d байт", fb->width, fb->height, fb->len);

    // Обов'язкове повернення буфера у драйвер для подальшого використання DMA
    esp_camera_fb_return(fb);
}
