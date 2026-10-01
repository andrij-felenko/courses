#include "esp_camera.h"
#include "esp_log.h"

static const char *TAG = "camera_diag";

esp_err_t init_camera_with_recovery(camera_config_t *config) {
    esp_err_t err = esp_camera_init(config);
    if (err == ESP_OK) {
        return ESP_OK;
    }

    ESP_LOGE(TAG, "Помилка ініціалізації камери: 0x%x", err);
    if (err == ESP_ERR_NOT_FOUND) {
        ESP_LOGE(TAG, "Сенсор OV3640 не знайдено на шині SCCB. Перевірте XCLK та живлення.");
    } else if (err == ESP_ERR_NO_MEM) {
        ESP_LOGE(TAG, "Нестача пам'яті для кадрового буфера.");
    }

    // Відновлення: звільняємо ресурси, знижуємо XCLK та повторюємо спробу
    esp_camera_deinit();
    config->xclk_freq_hz = 10000000; // 10 МГц замість 20 МГц
    return esp_camera_init(config);
}
