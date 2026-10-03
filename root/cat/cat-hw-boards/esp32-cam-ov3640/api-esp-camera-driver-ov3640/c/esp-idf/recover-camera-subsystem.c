#include "esp_camera.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "cam_recovery";

esp_err_t recover_camera_subsystem(const camera_config_t *config) {
    ESP_LOGW(TAG, "Спроба відновлення системи камери...");
    esp_camera_deinit();

    // Перезапуск живлення через вивід PWDN (якщо підключено)
    if (config->pin_pwdn >= 0) {
        gpio_set_level(config->pin_pwdn, 1);
        vTaskDelay(pdMS_TO_TICKS(100));
        gpio_set_level(config->pin_pwdn, 0);
        vTaskDelay(pdMS_TO_TICKS(100));
    }

    esp_err_t err = esp_camera_init(config);
    if (err == ESP_OK) {
        ESP_LOGI(TAG, "Систему камери успішно відновлено");
    } else {
        ESP_LOGE(TAG, "Не вдалося відновити камеру: 0x%x", err);
    }
    return err;
}
