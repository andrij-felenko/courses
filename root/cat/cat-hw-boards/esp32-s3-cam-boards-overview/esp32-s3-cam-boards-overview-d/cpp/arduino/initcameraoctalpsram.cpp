#include "esp_camera.h"

bool initCameraOctalPSRAM() {
    camera_config_t config;
    config.pin_pwdn = -1;
    config.pin_reset = -1;
    config.pin_xclk = 10;
    config.pin_sccb_sda = 40;
    config.pin_sccb_scl = 39;
    config.pin_d7 = 48;
    config.pin_d6 = 11;
    config.pin_d5 = 12;
    config.pin_d4 = 14;
    config.pin_d3 = 16;
    config.pin_d2 = 18;
    config.pin_d1 = 17;
    config.pin_d0 = 15;
    config.pin_vsync = 38;
    config.pin_href = 47;
    config.pin_pclk = 13;
    config.xclk_freq_hz = 20000000;
    config.ledc_timer = LEDC_TIMER_0;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.pixel_format = PIXFORMAT_RGB565;
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 12;
    config.fb_count = 2;
    config.grab_mode = CAMERA_GRAB_LATEST;
    config.fb_location = CAMERA_FB_IN_PSRAM;

    if (psramFound()) {
        Serial.print("Виявлено PSRAM обсягом: ");
        Serial.println(ESP.getPsramSize());
    } else {
        Serial.println("Помилка: PSRAM не виявлено на платі!");
        return false;
    }

    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Помилка ініціалізації камери: 0x%x\n", err);
        return false;
    }
    return true;
}
