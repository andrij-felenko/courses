#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_http_client.h"

#define MAX_RETRY_ATTEMPTS  5
#define BASE_DELAY_MS       1000

static const char *TAG = "FOTA_RETRY";

esp_err_t perform_fota_download_with_backoff(const char *url) {
    esp_http_client_config_t config = {
        .url = url,
        .timeout_ms = 5000,
    };
    
    for (int attempt = 0; attempt < MAX_RETRY_ATTEMPTS; attempt++) {
        esp_http_client_handle_t client = esp_http_client_init(&config);
        esp_err_t err = esp_http_client_perform(client);
        
        if (err == ESP_OK) {
            ESP_LOGI(TAG, "Успішно підключено до FOTA-сервера");
            esp_http_client_cleanup(client);
            return ESP_OK;
        }
        
        esp_http_client_cleanup(client);
        
        uint32_t delay_ms = BASE_DELAY_MS << attempt;
        ESP_LOGW(TAG, "Спроба %d не вдалася (помилка 0x%x). Очікування %u мс...", 
                 attempt + 1, err, delay_ms);
        vTaskDelay(pdMS_TO_TICKS(delay_ms));
    }
    
    ESP_LOGE(TAG, "Вичерпано максимальну кількість спроб підключення FOTA");
    return ESP_FAIL;
}
