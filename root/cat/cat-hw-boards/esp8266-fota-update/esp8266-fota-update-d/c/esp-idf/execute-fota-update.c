#include "esp_ota_ops.h"
#include "esp_http_client.h"
#include "esp_log.h"

// Функція виконання FOTA-оновлення через ESP-IDF OTA API
esp_err_t execute_fota_update(const char *stream_url) {
    esp_http_client_config_t config = {
        .url = stream_url,
        .timeout_ms = 5000,
    };
    
    esp_https_ota_config_t ota_config = {
        .http_config = &config,
    };

    ESP_LOGI("OTA", "Старт завантаження прошивки з %s", stream_url);
    esp_err_t ret = esp_https_ota(&ota_config);
    if (ret == ESP_OK) {
        ESP_LOGI("OTA", "Оновлення успішно записано. Перезавантаження...");
        esp_restart();
    } else {
        ESP_LOGE("OTA", "Збій завантаження прошивки, код помилки: 0x%x", ret);
    }
    return ret;
}
