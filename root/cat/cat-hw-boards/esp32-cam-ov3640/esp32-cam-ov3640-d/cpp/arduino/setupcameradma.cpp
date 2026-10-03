#include "esp_camera.h"

// Конфігурація камери для середовища Arduino IDE
void setupCameraDMA() {
  camera_config_t config;
  config.pin_pwdn     = 32;
  config.pin_reset    = -1;
  config.pin_xclk     = 0;
  config.pin_sccb_sda = 26;
  config.pin_sccb_scl = 27;

  config.pin_d7       = 35;
  config.pin_d6       = 34;
  config.pin_d5       = 39;
  config.pin_d4       = 36;
  config.pin_d3       = 21;
  config.pin_d2       = 19;
  config.pin_d1       = 18;
  config.pin_d0       = 5;
  config.pin_vsync    = 25;
  config.pin_href     = 23;
  config.pin_pclk     = 22;

  config.xclk_freq_hz = 20000000;
  config.ledc_timer   = LEDC_TIMER_0;
  config.ledc_channel = LEDC_CHANNEL_0;

  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size   = FRAMESIZE_UXGA;     // Надвисока роздільність UXGA (1600x1200)
  config.jpeg_quality = 10;
  config.fb_count     = 2;                  // Подвійна буферизація у PSRAM
  config.grab_mode    = CAMERA_GRAB_LATEST;
  config.fb_location  = CAMERA_FB_IN_PSRAM;

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Помилка ініціалізації камери: 0x%x\n", err);
    return;
  }
}

void loopCapture() {
  // Захоплення кадру через DMA без блокування основного циклу
  camera_fb_t * fb = esp_camera_fb_get();
  if (fb) {
    Serial.printf("Кадрова пам'ять DMA: %u байтів\n", fb->len);
    // Звільнення дескриптора буфера
    esp_camera_fb_return(fb);
  }
}
