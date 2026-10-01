#include "esp_camera.h"

void setupSensorDirectly() {
    sensor_t *s = esp_camera_sensor_get();
    if (!s) {
        return;
    }

    // Дзеркалювання кадру
    s->set_hmirror(s, 1);
    s->set_vflip(s, 1);

    // Вимкнення авто-експозиції AEC та ручне налаштування
    s->set_exposure_ctrl(s, 0);
    s->set_aec_value(s, 300);

    // Зчитування значення регістру через SCCB
    int reg_val = s->get_reg(s, 0x3000, 0xFF);
}
