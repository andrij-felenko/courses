#include "esp_ota_ops.h"
#include "esp_https_ota.h"
#include "esp_log.h"

static const char *TAG = "FOTA";

void perform_fota_update(const char *url) {
    esp_http_client_config_t config = {
        .url = url,
        .timeout_ms = 5000,
    };
    esp_https_ota_config_t ota_config = {
        .http_config = &config,
    };

    esp_err_t ret = esp_https_ota(&ota_config);
    if (ret == ESP_OK) {
        ESP_LOGI(TAG, "FOTA успішно завантажено. Перезапуск...");
        esp_restart();
    } else {
        ESP_LOGE(TAG, "Помилка FOTA оновлення: %d", ret);
    }
}

void mark_app_valid(void) {
    const esp_partition_t *running = esp_ota_get_running_partition();
    esp_ota_img_states_t ota_state;
    if (esp_ota_get_state_partition(running, &ota_state) == ESP_OK) {
        if (ota_state == ESP_OTA_IMG_PENDING_VERIFY) {
            esp_ota_mark_app_valid_cancel_rollback();
            ESP_LOGI(TAG, "Прошивка підтверджена як валідна.");
        }
    }
}
