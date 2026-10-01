#include "esp_ota_ops.h"
#include "esp_http_client.h"
#include "esp_https_ota.h"

// Функція виконує оновлення прошивки в середовищі ESP-IDF
esp_err_t start_esp_idf_ota(const char* url) {
    esp_http_client_config_t http_config = {
        .url = url,
        .cert_pem = NULL, // Для тестування без перевірки сертифіката
    };
    
    esp_https_ota_config_t ota_config = {
        .http_config = &http_config,
    };

    // Виконання повного циклу FOTA
    esp_err_t ret = esp_https_ota(&ota_config);
    if (ret == ESP_OK) {
        esp_restart();
    }
    return ret;
}
