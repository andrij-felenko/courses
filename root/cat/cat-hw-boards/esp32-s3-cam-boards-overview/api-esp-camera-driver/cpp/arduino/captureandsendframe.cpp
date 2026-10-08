#include "esp_camera.h"

void captureAndSendFrame() {
  camera_fb_t* fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Помилка: вказівник кадрового буфера NULL");
    return;
  }

  // Робота з даними кадру
  Serial.printf("Розмір кадру: %zu B, формат: %d\n", fb->len, fb->format);

  // Обов'язкове звільнення буфера
  esp_camera_fb_return(fb);
  fb = nullptr;
}
