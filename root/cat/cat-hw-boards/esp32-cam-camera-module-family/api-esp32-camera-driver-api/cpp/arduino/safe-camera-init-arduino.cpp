#include "esp_camera.h"

bool safe_camera_init_arduino(camera_config_t *config) {
    esp_err_t err = esp_camera_init(config);
    if (err != ESP_OK) {
        Serial.printf("Помилка ініціалізації камери: 0x%x\n", err);
        if (err == ESP_ERR_NO_MEM) {
            Serial.println("Причина: нестача пам'яті PSRAM/SRAM.");
        } else if (err == ESP_ERR_NOT_FOUND) {
            Serial.println("Причина: сенсор не відповідає по шині SCCB.");
        }
        return false;
    }
    Serial.println("Ініціалізація камери пройшла успішно!");
    return true;
}
