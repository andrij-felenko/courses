#include "esp_https_ota.h"
#include "esp_log.h"

esp_err_t validate_image_header(esp_app_desc_t *new_app_info) {
    ESP_LOGI("OTA", "Версія нової прошивки: %s", new_app_info->version);
    return ESP_OK;
}

void run_native_https_ota(const char* url) {
    esp_http_client_config_t config = {
        .url = url,
        .cert_pem = NULL, // Приймається CA сертифікат
    };
    esp_https_ota_config_t ota_config = {
        .http_config = &config,
    };
    
    esp_err_t ret = esp_https_ota(&ota_config);
    if (ret == ESP_OK) {
        esp_restart();
    } else {
        ESP_LOGE("OTA", "Нативний виклик HTTPS OTA завершився помилкою %d", ret);
    }
}
