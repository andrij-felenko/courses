#include "esp_camera.h"
#include "esp_log.h"

static const char *TAG = "camera_diag";

// Алгоритм ініціалізації з розширеною обробкою кодів помилок
esp_err_t init_camera_with_diagnostics(const camera_config_t *config) {
    esp_err_t err = esp_camera_init(config);
    if (err != ESP_OK) {
        if (err == ESP_ERR_NOT_FOUND) {
            ESP_LOGE(TAG, "Сенсор OV3640 не знайдено на шині SCCB. Перевірте XCLK та SIOC/SIOD");
        } else if (err == ESP_ERR_NO_MEM) {
            ESP_LOGE(TAG, "Недостатньо RAM для виділення кадрових буферів. Зменшіть frame_size або fb_count");
        } else if (err == ESP_ERR_TIMEOUT) {
            ESP_LOGE(TAG, "Таймаут виділення ресурсів DMA або таймера LEDC");
        } else {
            ESP_LOGE(TAG, "Помилка ініціалізації камери: 0x%x", err);
        }
        return err;
    }
    ESP_LOGI(TAG, "Драйвер камери успішно ініціалізовано");
    return ESP_OK;
}
