#include "esp_camera.h"

void capture_and_process_frame() {
    // Захоплення покадрового буфера
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("Помилка прийому кадру камери");
        return;
    }

    Serial.printf("Захоплено кадр: %u байт, %ux%u\n", fb->len, fb->width, fb->height);

    // Звільнення буфера для наступних циклів DMA
    esp_camera_fb_return(fb);
}
