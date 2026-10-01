#include "esp_camera.h"

void captureAndProcessFrame()
{
    // Отримання вказівника на кадр
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("Не вдалося отримати кадр");
        return;
    }

    Serial.printf("Розмір кадру: %u байт\n", (unsigned int)fb->len);

    // Звільнення пам'яті кадрового буфера
    esp_camera_fb_return(fb);
}
