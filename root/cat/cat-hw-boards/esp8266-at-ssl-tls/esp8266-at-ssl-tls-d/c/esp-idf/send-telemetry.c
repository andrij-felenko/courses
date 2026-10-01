#include "esp_log.h"
#include "esp_http_client.h"

// Приклад відправлення HTTPS POST-запиту через C API ESP-IDF
void send_telemetry(const char* payload) {
    esp_http_client_config_t config = {
        .url = "https://api.example.com/api/v1/data",
        .crt_bundle_attach = esp_crt_bundle_attach,
    };
    esp_http_client_handle_t client = esp_http_client_init(&config);
    esp_http_client_set_method(client, HTTP_METHOD_POST);
    esp_http_client_set_post_field(client, payload, strlen(payload));
    esp_err_t err = esp_http_client_perform(client);
    if (err == ESP_OK) {
        ESP_LOGI("HTTPS", "Статус відповіді: %d", esp_http_client_get_status_code(client));
    }
    esp_http_client_cleanup(client);
}
