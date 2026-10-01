#include "esp_camera.h"

bool enableTestPattern() {
    sensor_t *s = esp_camera_sensor_get();
    if (s == nullptr) {
        return false;
    }
    // Переключення на банк регістрів 1 (Sensor Core)
    if (s->set_reg(s, 0xFF, 0xFF, 0x01) != 0) {
        return false;
    }
    // Ввімкнення біта тестового патерну у регістрі 0x12 (маска 0x02)
    if (s->set_reg(s, 0x12, 0x02, 0x02) != 0) {
        return false;
    }
    return true;
}
