#include "esp_camera.h"
#include "esp_log.h"

static const char *TAG = "sensor_config";

esp_err_t configure_ov3640_dynamic(void)
{
    sensor_t *s = esp_camera_sensor_get();
    if (!s) {
        ESP_LOGE(TAG, "Вказівник на sensor_t є пошкодженим або не ініціалізовано драйвер");
        return ESP_FAIL;
    }

    // Встановлення дзеркального відображення та орієнтації
    s->set_hmirror(s, 1);
    s->set_vflip(s, 1);

    // Увімкнення автоматичної експозиції (AEC) та автоматичного підсилення (AGC)
    s->set_exposure_ctrl(s, 1);
    s->set_gain_ctrl(s, 1);

    // Прямий запис у 16-бітний регістр OV3640 через шину SCCB для тонкої корекції
    // Наприклад, регістр 0x3300 відповідає за внутрішнє конфігурування підсилення DSP
    int res = s->set_reg(s, 0x3300, 0xFF, 0x1A);
    if (res != 0) {
        ESP_LOGW(TAG, "Не вдалося записати регістр 0x3300 через SCCB");
    }

    ESP_LOGI(TAG, "Динамічне налаштування сенсора успішно застосовано");
    return ESP_OK;
}
