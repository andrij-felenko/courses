// Зміна параметрів зображення через сенсорний інтерфейс в ESP-IDF
#include "esp_camera.h"
#include "esp_log.h"

esp_err_t adjust_sensor_settings(int brightness, bool flip_vertical) {
    sensor_t *s = esp_camera_sensor_get();
    if (!s) {
        ESP_LOGE("SENSOR", "Не вдалося отримати вказівник на сенсор");
        return ESP_FAIL;
    }

    // Встановлення нової яскравості та орієнтації
    s->set_brightness(s, brightness);
    s->set_vflip(s, flip_vertical ? 1 : 0);

    return ESP_OK;
}
