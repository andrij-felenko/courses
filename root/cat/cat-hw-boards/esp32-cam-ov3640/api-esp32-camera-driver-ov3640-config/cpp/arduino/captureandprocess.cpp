#include "esp_camera.h"

void captureAndProcess() {
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Помилка ініціалізації камери: 0x%x\n", err);
        return;
    }

    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("Не вдалося отримати буфер кадру");
        return;
    }

    Serial.printf("Кадр отримано: %u байт, розмір %ux%u\n", fb->len, fb->width, fb->height);

    // Обробка кадру або передача даних...

    esp_camera_fb_return(fb);
}
