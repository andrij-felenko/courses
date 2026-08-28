// ESP8266 RTOS SDK (ESP-IDF-стиль): те саме, але блимання — окрема задача FreeRTOS,
// тож блокувальна пауза в ній нікому не заважає.
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "esp_http_server.h"
#include "nvs_flash.h"
#include "tcpip_adapter.h"

#define LED_GPIO   GPIO_NUM_2       // катод світлодіода тут: 0 -> світить, 1 -> гасне
#define BLINK_MS   1000

static const char *TAG = "esp01";
static bool led_on = false;

// Блимання власною задачею: vTaskDelay присипляє ЛИШЕ її, сервер працює далі
static void blink_task(void *arg) {
    for (;;) {
        led_on = !led_on;
        gpio_set_level(LED_GPIO, led_on ? 0 : 1);
        vTaskDelay(pdMS_TO_TICKS(BLINK_MS));
    }
}

// Обробник кореневої сторінки: віддаємо стан коротким HTML
static esp_err_t root_get(httpd_req_t *req) {
    uint32_t up_sec = xTaskGetTickCount() * portTICK_PERIOD_MS / 1000;
    char html[256];
    int n = snprintf(html, sizeof(html),
        "<!DOCTYPE html><html><head><meta charset='utf-8'><title>ESP-01</title>"
        "</head><body><h2>ESP-01 живий</h2><p>Працює: %u с</p>"
        "<p>Світлодіод: %s</p></body></html>",
        (unsigned) up_sec, led_on ? "увімкнено" : "вимкнено");
    httpd_resp_set_type(req, "text/html; charset=utf-8");
    return httpd_resp_send(req, html, n);
}

// Адресу дає стек — подією, а не поверненням функції приєднання
static void on_got_ip(void *arg, esp_event_base_t base, int32_t id, void *data) {
    ip_event_got_ip_t *e = (ip_event_got_ip_t *) data;
    ESP_LOGI(TAG, "Приєднано. IP: " IPSTR, IP2STR(&e->ip_info.ip));

    static httpd_handle_t srv = NULL;
    httpd_config_t cfg = HTTPD_DEFAULT_CONFIG();
    if (httpd_start(&srv, &cfg) == ESP_OK) {
        httpd_uri_t root = { .uri = "/", .method = HTTP_GET,
                             .handler = root_get, .user_ctx = NULL };
        httpd_register_uri_handler(srv, &root);
        ESP_LOGI(TAG, "Веб-сервер запущено");
    }
}

void app_main(void) {
    ESP_ERROR_CHECK(nvs_flash_init());     // Wi-Fi зберігає калібрування у NVS
    tcpip_adapter_init();
    ESP_ERROR_CHECK(esp_event_loop_create_default());

    gpio_config_t io = {
        .pin_bit_mask = 1ULL << LED_GPIO,
        .mode         = GPIO_MODE_OUTPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&io));
    gpio_set_level(LED_GPIO, 1);           // старт: вимкнено

    ESP_ERROR_CHECK(esp_event_handler_register(
        IP_EVENT, IP_EVENT_STA_GOT_IP, &on_got_ip, NULL));

    wifi_init_config_t wcfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&wcfg));
    wifi_config_t sta = { .sta = { .ssid = "MyHomeWiFi", .password = "supersecret" } };
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));   // режим клієнта
    ESP_ERROR_CHECK(esp_wifi_set_config(ESP_IF_WIFI_STA, &sta));
    ESP_ERROR_CHECK(esp_wifi_start());
    ESP_ERROR_CHECK(esp_wifi_connect());

    xTaskCreate(blink_task, "blink", 2048, NULL, 5, NULL);
}
