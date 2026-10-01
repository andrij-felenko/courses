#include "esp_camera.h"

bool safeCameraInit(camera_config_t &config) {
    esp_err_t err = esp_camera_init(&config);
    if (err == ESP_OK) {
        return true;
    }

    Serial.printf("Помилка камери: 0x%X\n", err);
    esp_camera_deinit();

    // При нестачі пам'яті зменшуємо кількість буферів до 1
    if (err == ESP_ERR_NO_MEM && config.fb_count > 1) {
        config.fb_count = 1;
        return (esp_camera_init(&config) == ESP_OK);
    }
    return false;
}
