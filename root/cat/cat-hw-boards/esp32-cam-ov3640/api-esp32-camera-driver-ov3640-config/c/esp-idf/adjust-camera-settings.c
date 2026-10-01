#include "esp_camera.h"
#include "esp_log.h"

static const char *TAG = "cam_tune";

void adjust_camera_settings(void) {
    sensor_t *s = esp_camera_sensor_get();
    if (!s) {
        ESP_LOGE(TAG, "Сенсор не ініціалізовано");
        return;
    }

    // Налаштування параметрів зображення
    s->set_brightness(s, 1);     // Підвищення яскравості
    s->set_contrast(s, 1);       // Підвищення контрасту
    s->set_whitebal(s, 1);       // Увімкнення AWB
    s->set_hmirror(s, 1);        // Дзеркалювання по горизонталі
    s->set_vflip(s, 1);          // Перевертання по вертикалі
}
