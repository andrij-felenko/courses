#include "esp_camera.h"
#include "esp_log.h"

static const char *TAG = "sensor_config";

esp_err_t configure_sensor_settings(void) {
    // Отримання вказівника на структуру керування сенсором
    sensor_t *s = esp_camera_sensor_get();
    if (!s) {
        ESP_LOGE(TAG, "Не вдалося отримати дескриптор sensor_t");
        return ESP_FAIL;
    }

    // Динамічне змінення роздільної здатності та якості стиснення
    s->set_framesize(s, FRAMESIZE_VGA);
    s->set_quality(s, 12);

    // Встановлення дзеркалювання та автоматичного балансу білого
    s->set_hmirror(s, 1);
    s->set_vflip(s, 1);
    s->set_whitebal(s, 1);
    s->set_exposure_ctrl(s, 1);

    return ESP_OK;
}
