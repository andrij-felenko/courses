#include "esp_camera.h"

bool setupCameraSafe(const camera_config_t &config) {
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        if (err == ESP_ERR_NOT_FOUND) {
            Serial.println("Помилка: сенсор OV3640 не знайдено на шині SCCB");
        } else if (err == ESP_ERR_NO_MEM) {
            Serial.println("Помилка: бракує пам'яті DRAM/PSRAM для кадрових буферів");
        } else if (err == ESP_ERR_INVALID_STATE) {
            Serial.println("Помилка: драйвер камери вже запущено");
        } else {
            Serial.printf("Помилка ініціалізації камери: 0x%x\n", err);
        }
        return false;
    }
    return true;
}
