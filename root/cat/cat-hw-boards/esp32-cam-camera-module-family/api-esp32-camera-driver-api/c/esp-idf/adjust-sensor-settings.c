#include "esp_log.h"
#include "esp_camera.h"

static const char *TAG = "sensor_ctrl";

esp_err_t adjust_sensor_settings(int brightness, bool flip) {
    sensor_t *s = esp_camera_sensor_get();
    if (!s) {
        ESP_LOGE(TAG, "Сенсор камери не знайдено");
        return ESP_ERR_NOT_FOUND;
    }

    // Динамічне коригування параметрів зображення
    s->set_brightness(s, brightness); // діапазон від -2 до 2
    s->set_vflip(s, flip ? 1 : 0);      // вертикальний переворот
    s->set_hmirror(s, flip ? 1 : 0);    // горизонтальне дзеркалювання
    
    ESP_LOGI(TAG, "Налаштування сенсора успішно застосовано");
    return ESP_OK;
}
