// Динамічне налаштування параметрів камери в ESP-IDF
#include "esp_camera.h"

esp_err_t reconfigure_camera_sensor(void) {
    sensor_t *s = esp_camera_sensor_get();
    if (!s) {
        return ESP_FAIL;
    }
    // Встановлення роздільності VGA (640x480)
    s->set_framesize(s, FRAMESIZE_VGA);
    // Увімкнення горизонтального дзеркалювання
    s->set_hmirror(s, 1);
    // Налаштування контрасту та яскравості
    s->set_contrast(s, 1);
    s->set_brightness(s, 0);
    // Конфігурація автоекспозиції
    s->set_gain_ceiling(s, GAINCEILING_4X);
    return ESP_OK;
}
