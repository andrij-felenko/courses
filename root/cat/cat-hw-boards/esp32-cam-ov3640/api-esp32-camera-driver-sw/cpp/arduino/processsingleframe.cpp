// Цикл зйомки з автоматичною гарантією повернення кадрового буфера у середовищі Arduino
#include "esp_camera.h"
#include <Arduino.h>

void processSingleFrame() {
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("Помилка захоплення кадру");
        return;
    }

    Serial.printf("Кадр отримано: %u байт\n", (unsigned int)fb->len);

    // Повернення буфера назад у пул драйвера
    esp_camera_fb_return(fb);
}
