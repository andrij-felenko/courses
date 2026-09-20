#include "esp_http_client.h"
#include "esp_wifi.h"

void send_to_server(const uint8_t* payload, size_t length) {
    esp_http_client_config_t config = {
        .url = "http://api.myserver.com/data",
    };
    esp_http_client_handle_t client = esp_http_client_init(&config);

    esp_http_client_set_method(client, HTTP_METHOD_POST);
    esp_http_client_set_header(client, "Content-Type", "application/octet-stream");
    esp_http_client_set_post_field(client, (const char*)payload, length);

    esp_http_client_perform(client);
    esp_http_client_cleanup(client);
}
