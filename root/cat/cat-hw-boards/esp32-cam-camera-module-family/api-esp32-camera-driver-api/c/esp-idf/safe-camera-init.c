#include "esp_log.h"
#include "esp_camera.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "cam_err_handle";

esp_err_t safe_camera_init(const camera_config_t *config) {
    esp_err_t err = esp_camera_init(config);
    if (err != ESP_OK) {
        if (err == ESP_ERR_NO_MEM) {
            ESP_LOGE(TAG, "Нестача пам'яті! Перевірте наявність PSRAM або зменшіть роздільну здатність.");
        } else if (err == ESP_ERR_NOT_FOUND) {
            ESP_LOGE(TAG, "Камеру не виявлено! Перевірте шину SCCB та тактування XCLK.");
        } else {
            ESP_LOGE(TAG, "Помилка ініціалізації камери: 0x%x", err);
        }
        return err;
    }
    ESP_LOGI(TAG, "Драйвер камери успішно ініціалізовано");
    return ESP_OK;
}
