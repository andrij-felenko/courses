#include "esp_camera.h"
#include "Arduino.h"

void captureAndProcessFrame() {
  // 1. Отримання буфера кадру
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Помилка захоплення кадру!");
    return;
  }

  // 2. Обробка зображення
  Serial.printf("Розмір кадру: %d байтів, Роздільність: %dx%d\n", 
                fb->len, fb->width, fb->height);

  // 3. Обов'язкове вивільнення буфера
  esp_camera_fb_return(fb);
  fb = NULL;
}

void loop() {
  captureAndProcessFrame();
  delay(100);
}
