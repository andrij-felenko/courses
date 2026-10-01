#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "esp_http_client.h"
#include "driver/gpio.h"

#define SENSOR_GPIO GPIO_NUM_2
#define WIFI_SSID "WiFi_Network"
#define WIFI_PASS "SecretPassword"

static const char *TAG = "SENSOR_NODE";

static esp_err_t _http_event_handler(esp_http_client_event_t *evt) {
    return ESP_OK;
}

void send_sensor_data(float temperature, float humidity) {
    char post_data[64];
    snprintf(post_data, sizeof(post_data), "{\"temperature\":%.1f,\"humidity\":%.1f}", temperature, humidity);

    esp_http_client_config_t config = {
        .url = "http://192.168.1.100/api/data",
        .event_handler = _http_event_handler,
    };
    esp_http_client_handle_t client = esp_http_client_init(&config);
    esp_http_client_set_method(client, HTTP_METHOD_POST);
    esp_http_client_set_header(client, "Content-Type", "application/json");
    esp_http_client_set_post_field(client, post_data, strlen(post_data));

    esp_err_t err = esp_http_client_perform(client);
    if (err == ESP_OK) {
        ESP_LOGI(TAG, "HTTP POST status: %d", esp_http_client_get_status_code(client));
    }
    esp_http_client_cleanup(client);
}

void app_main(void) {
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    gpio_set_direction(SENSOR_GPIO, GPIO_MODE_INPUT);

    while (1) {
        float temp = 23.5f;
        float hum = 55.0f;
        send_sensor_data(temp, hum);
        vTaskDelay(pdMS_TO_TICKS(10000));
    }
}
