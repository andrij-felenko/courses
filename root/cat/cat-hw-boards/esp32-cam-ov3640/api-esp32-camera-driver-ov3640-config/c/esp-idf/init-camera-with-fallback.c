#include "esp_camera.h"
#include "esp_log.h"

static const char *TAG = "camera_diag";

esp_err_t init_camera_with_fallback(camera_config_t *config)
{
    esp_err_t err = esp_camera_init(config);
    if (err == ESP_ERR_NOT_FOUND) {
        ESP_LOGE(TAG, "OV3640 не знайдено на шині SCCB. Перевірте лінії SIOC/SIOD та живлення 2.8V");
        return err;
    } else if (err == ESP_ERR_NO_MEM) {
        ESP_LOGE(TAG, "Нестача пам'яті PSRAM під кадрові буфери");
        return err;
    } else if (err != ESP_OK) {
        ESP_LOGW(TAG, "Спроба ініціалізації на 20 МГц не вдалася (код 0x%x). Знижуємо XCLK до 10 МГц", err);
        config->xclk_freq_hz = 10000000;
        err = esp_camera_init(config);
    }

    if (err == ESP_OK) {
        ESP_LOGI(TAG, "Драйвер успішно ініціалізовано на частоті %d МГц", config->xclk_freq_hz / 1000000);
    }
    return err;
}
