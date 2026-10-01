#include "esp_camera.h"
#include "esp_log.h"

static const char *TAG = "sensor_ctrl";

esp_err_t configure_sensor_dsp(void) {
    sensor_t *s = esp_camera_sensor_get();
    if (!s) {
        ESP_LOGE(TAG, "Не вдалося отримати вказівник на sensor_t");
        return ESP_FAIL;
    }

    // Встановлення якості JPEG стиснення
    s->set_quality(s, 12);

    // Увімкнення автоматичних режимів AEC та AWB
    s->set_exposure_ctrl(s, 1);
    s->set_whitebal(s, 1);
    s->set_gain_ctrl(s, 1);

    // Вертикальний розворот кадру
    s->set_vflip(s, 1);

    ESP_LOGI(TAG, "DSP OV3640 успішно налаштовано");
    return ESP_OK;
}
