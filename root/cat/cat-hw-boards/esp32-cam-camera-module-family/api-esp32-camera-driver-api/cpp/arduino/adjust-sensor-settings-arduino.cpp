#include "esp_camera.h"

void adjust_sensor_settings_arduino(int brightness, bool flip) {
    sensor_t *s = esp_camera_sensor_get();
    if (!s) {
        Serial.println("Помилка: покажчик sensor_t дорівнює NULL");
        return;
    }

    // Встановлення яскравості та дзеркалювання
    s->set_brightness(s, brightness);
    s->set_vflip(s, flip ? 1 : 0);
    s->set_hmirror(s, flip ? 1 : 0);
    Serial.println("Сенсор переналаштовано на льоту");
}
