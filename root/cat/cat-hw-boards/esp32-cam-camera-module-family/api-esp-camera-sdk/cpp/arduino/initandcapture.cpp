#include "esp_camera.h"
#include "Arduino.h"

bool initAndCapture(const camera_config_t &config) {
    if (psramFound() && psramGetFreeSpace() < (1024 * 1024)) {
        Serial.println("Брак PSRAM для стабільної роботи");
        return false;
    }

    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Помилка камери: 0x%x\n", err);
        return false;
    }

    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("Збій отримання кадрового буфера");
        return false;
    }

    // Обробка кадру...

    esp_camera_fb_return(fb);
    return true;
}
