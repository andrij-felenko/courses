#include "esp_camera.h"

void capture_frame_arduino() {
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Помилка ініціалізації камери: 0x%x\n", err);
    return;
  }

  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Не вдалося отримати кадр");
    return;
  }

  Serial.printf("Захоплено кадр: %zu байт\n", fb->len);

  // Обов'язкове повернення кадрового буфера
  esp_camera_fb_return(fb);
}
