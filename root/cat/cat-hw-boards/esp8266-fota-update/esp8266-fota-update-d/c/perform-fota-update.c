#include "esp_http_client.h"
#include "esp_ota_ops.h"

// Обробка оновлення прошивки по HTTP у середовищі ESP-IDF
esp_err_t perform_fota_update(const char *url) {
    esp_http_client_config_t config = {
        .url = url,
        .timeout_ms = 5000,
    };
    esp_err_t ret = esp_https_ota(&config);
    if (ret == ESP_OK) {
        esp_restart();
    }
    return ret;
}
