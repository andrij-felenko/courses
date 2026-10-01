#include "esp_camera.h"

esp_err_t enable_test_pattern(void) {
    sensor_t *s = esp_camera_sensor_get();
    if (!s) {
        return ESP_ERR_INVALID_STATE;
    }
    // Переключення на банк регістрів 1 (Sensor Core)
    if (s->set_reg(s, 0xFF, 0xFF, 0x01) != 0) {
        return ESP_FAIL;
    }
    // Ввімкнення біта тестового патерну у регістрі 0x12 (маска 0x02)
    if (s->set_reg(s, 0x12, 0x02, 0x02) != 0) {
        return ESP_FAIL;
    }
    return ESP_OK;
}
