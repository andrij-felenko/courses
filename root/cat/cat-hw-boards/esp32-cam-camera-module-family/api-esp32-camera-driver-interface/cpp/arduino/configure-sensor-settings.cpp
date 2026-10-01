#include "esp_camera.h"

bool configure_sensor_settings() {
    // Отримання дескриптора фотоматриці
    sensor_t *s = esp_camera_sensor_get();
    if (!s) {
        Serial.println("Помилка отримання вказівника на sensor_t");
        return false;
    }

    // Зміна роздільності та рівня стиснення JPEG
    s->set_framesize(s, FRAMESIZE_VGA);
    s->set_quality(s, 12);

    // Налаштування орієнтації та експозиції
    s->set_hmirror(s, 1);
    s->set_vflip(s, 1);
    s->set_whitebal(s, 1);
    s->set_exposure_ctrl(s, 1);

    return true;
}
