#include "esp_camera.h"
#include "esp_log.h"

namespace {
constexpr const char *TAG = "sensor_config_cpp";
}

esp_err_t configure_ov3640_dynamic_cpp()
{
    sensor_t *s = esp_camera_sensor_get();
    if (s == nullptr) {
        ESP_LOGE(TAG, "Помилка: об'єкт sensor_t недоступний");
        return ESP_FAIL;
    }

    // Адаптація параметрів зображення вказівниками функцій sensor_t
    s->set_hmirror(s, 1);
    s->set_vflip(s, 1);
    s->set_exposure_ctrl(s, 1);
    s->set_gain_ctrl(s, 1);

    // Пряме керування 16-бітними регістрами через SCCB
    if (s->set_reg(s, 0x3300, 0xFF, 0x1A) != 0) {
        ESP_LOGW(TAG, "SCCB помилка запису у 16-бітний регістр 0x3300");
    }

    ESP_LOGI(TAG, "Сенсор успішно переналаштовано в реальному часі");
    return ESP_OK;
}
