#include "esp_camera.h"
#include "esp_log.h"

static const char *TAG = "camera_capture";

void capture_and_process_frame(void) {
    // Отримання кадрового буфера з черги DMA
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        ESP_LOGE(TAG, "Помилка захоплення кадру з фотоматриці");
        return;
    }

    // Обробка даних кадру
    ESP_LOGI(TAG, "Кадр отримано: %u байтів, роздільність %ux%u", (unsigned int)fb->len, (unsigned int)fb->width, (unsigned int)fb->height);

    // Обов'язкове повернення буфера назад у кільцеву чергу DMA
    esp_camera_fb_return(fb);
}
