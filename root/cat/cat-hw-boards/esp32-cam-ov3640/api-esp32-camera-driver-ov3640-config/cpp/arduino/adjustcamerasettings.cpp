#include "esp_camera.h"

void adjustCameraSettings() {
    sensor_t *s = esp_camera_sensor_get();
    if (!s) {
        Serial.println("Сенсор не ініціалізовано");
        return;
    }

    // Налаштування параметрів зображення
    s->set_brightness(s, 1);     // Підвищення яскравості
    s->set_contrast(s, 1);       // Підвищення контрасту
    s->set_whitebal(s, 1);       // Увімкнення AWB
    s->set_hmirror(s, 1);        // Дзеркалювання по горизонталі
    s->set_vflip(s, 1);          // Перевертання по вертикалі
}
