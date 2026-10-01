#include "esp_camera.h"
#include "esp_log.h"

static const char *TAG = "camera_init";

esp_err_t init_camera_safe(const camera_config_t *config) {
    esp_err_t err = esp_camera_init(config);
    if (err != ESP_OK) {
        if (err == ESP_ERR_NOT_FOUND) {
            ESP_LOGE(TAG, "Сенсор OV3640 не виявлено на шині SCCB. Перевірте живлення та GPIO sccb_sda/sccb_scl");
        } else if (err == ESP_ERR_NO_MEM) {
            ESP_LOGE(TAG, "Недостатньо пам'яті для буферів кадру. Зменшіть fb_count або використовуйте PSRAM");
        } else if (err == ESP_ERR_INVALID_STATE) {
            ESP_LOGE(TAG, "Драйвер камери вже ініціалізовано або порт I2C зайнятий");
        } else {
            ESP_LOGE(TAG, "Помилка ініціалізації камери: 0x%x", err);
        }
        return err;
    }
    return ESP_OK;
}
