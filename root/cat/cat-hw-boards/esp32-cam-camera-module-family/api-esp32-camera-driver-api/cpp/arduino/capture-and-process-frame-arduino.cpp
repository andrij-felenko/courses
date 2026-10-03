#include "esp_camera.h"

void capture_and_process_frame_arduino() {
    // 1. Запит кадрового буфера з драйвера
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("Помилка захоплення кадру");
        return;
    }

    // 2. Обробка кадру
    Serial.printf("Кадр отримано: %u байтів, роздільна здатність %dx%d\n", 
                  fb->len, fb->width, fb->height);

    // 3. Обов'язкове повернення буфера у пул DMA
    esp_camera_fb_return(fb);
}
