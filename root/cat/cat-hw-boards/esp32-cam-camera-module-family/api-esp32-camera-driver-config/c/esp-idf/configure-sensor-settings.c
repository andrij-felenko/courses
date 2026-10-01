#include "esp_camera.h"

void configure_sensor_settings(void) {
    sensor_t *s = esp_camera_sensor_get();
    if (s != NULL) {
        // Налаштування автоматичного підсилення та експозиції
        s->set_gain_ctrl(s, 1);       // Увімкнути AGC
        s->set_exposure_ctrl(s, 1);   // Увімкнути AEC
        s->set_awb_gain(s, 1);        // Увімкнути AWB

        // Корекція орієнтації зображення
        s->set_hmirror(s, 1);         // Дзеркалювання по горизонталі
        s->set_vflip(s, 1);           // Переворот по вертикалі

        // Налаштування контрасту та яскравості
        s->set_contrast(s, 1);        // Збільшити контраст (+1)
        s->set_brightness(s, 0);      // Нормальна яскравість (0)
    }
}
