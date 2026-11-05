#include "esp_camera.h"
#include "dl_detection_engine.hpp"

// Налаштування конвеєра інференсу у середовищі Arduino IDE для ESP32-S3
void setup_edge_ai() {
  psramInit();

  // Конфігурація камери та ініціалізація векторного прискорювача ESP-WHO
  dl::detect::HumanFaceDetect detector;
  camera_fb_t *fb = esp_camera_fb_get();

  if (fb && fb->format == PIXFORMAT_RGB565) {
    // Автоматичне перетворення кадрового буфера в тензор INT8
    auto boxes = detector.detect(fb);
    esp_camera_fb_return(fb);
  }
}
