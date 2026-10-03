#include "esp_camera.h"

void captureAndProcessFrame() {
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Помилка отримання кадру камери");
    return;
  }

  // Використання байтів кадру (наприклад, надсилання через HTTP/MQTT)
  Serial.printf("Розмір кадру: %u байтів, роздільність: %ux%u\n", fb->len, fb->width, fb->height);

  // Обов'язкове повернення буфера в пул DMA
  esp_camera_fb_return(fb);
}
