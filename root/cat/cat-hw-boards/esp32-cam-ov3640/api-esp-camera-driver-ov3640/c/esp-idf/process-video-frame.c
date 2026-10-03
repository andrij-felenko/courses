#include "esp_camera.h"
#include "esp_log.h"

static const char *TAG = "frame_processor";

void process_video_frame(void) {
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        ESP_LOGE(TAG, "Неможливо отримати кадр з камери");
        return;
    }

    // Обробка або передача даних кадру
    ESP_LOGI(TAG, "Отримано кадр: %zu байтів, %ux%u", fb->len, fb->width, fb->height);

    // Обов'язкове звільнення буфера кадру
    esp_camera_fb_return(fb);
}
