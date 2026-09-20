#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "esp_system.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "esp_http_server.h"

#include "relay_driver.h"
#include "wifi_manager.h"
#include "mqtt_app.h"

static const char *TAG = "MAIN_APP";

/* Глобальний дескриптор реле */
static relay_handle_t s_relay;

/* Глобальний дескриптор HTTP-сервера */
static httpd_handle_t s_web_server = NULL;

/**
 * @brief HTTP GET handler для головної сторінки "/"
 */
static esp_err_t http_root_handler(httpd_req_t *req)
{
    relay_state_t st = relay_driver_get_state(&s_relay);
    bool is_on = (st == RELAY_STATE_ON);

    char resp_str[1024];
    snprintf(resp_str, sizeof(resp_str),
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        "<title>ESP-01S Relay Module</title>"
        "<style>"
        "body{font-family:Helvetica,Arial,sans-serif;text-align:center;background:#1a1a1a;color:#eee;padding-top:40px;}"
        ".card{background:#2a2a2a;display:inline-block;padding:30px;border-radius:10px;box-shadow:0 4px 10px rgba(0,0,0,0.5);}"
        ".status{font-size:24px;font-weight:bold;margin:20px 0;color:%s;}"
        ".btn{display:inline-block;padding:12px 28px;font-size:16px;color:#fff;border:none;border-radius:5px;text-decoration:none;margin:8px;cursor:pointer;}"
        ".on{background:#28a745;}.off{background:#dc3545;}.toggle{background:#17a2b8;}"
        "</style></head><body>"
        "<div class='card'>"
        "<h2>ESP-01S Relay Controller (ESP-IDF / FreeRTOS)</h2>"
        "<p>Поточний стан котушки реле (GPIO0):</p>"
        "<div class='status'>%s</div>"
        "<div>"
        "<a href='/on' class='btn on'>Увімкнути (ON)</a>"
        "<a href='/off' class='btn off'>Вимкнути (OFF)</a>"
        "<a href='/toggle' class='btn toggle'>Переключити</a>"
        "</div>"
        "</div>"
        "</body></html>",
        is_on ? "#28a745" : "#dc3545",
        is_on ? "УВІМКНЕНО (ON)" : "ВИМКНЕНО (OFF)"
    );

    httpd_resp_set_type(req, "text/html");
    return httpd_resp_send(req, resp_str, HTTPD_RESP_USE_STRLEN);
}

/**
 * @brief HTTP GET handler для команди "/on"
 */
static esp_err_t http_on_handler(httpd_req_t *req)
{
    relay_driver_set_state(&s_relay, RELAY_STATE_ON);
    mqtt_app_publish_status(RELAY_STATE_ON);

    httpd_resp_set_status(req, "303 See Other");
    httpd_resp_set_hdr(req, "Location", "/");
    return httpd_resp_send(req, NULL, 0);
}

/**
 * @brief HTTP GET handler для команди "/off"
 */
static esp_err_t http_off_handler(httpd_req_t *req)
{
    relay_driver_set_state(&s_relay, RELAY_STATE_OFF);
    mqtt_app_publish_status(RELAY_STATE_OFF);

    httpd_resp_set_status(req, "303 See Other");
    httpd_resp_set_hdr(req, "Location", "/");
    return httpd_resp_send(req, NULL, 0);
}

/**
 * @brief HTTP GET handler для команди "/toggle"
 */
static esp_err_t http_toggle_handler(httpd_req_t *req)
{
    relay_driver_toggle(&s_relay);
    relay_state_t new_st = relay_driver_get_state(&s_relay);
    mqtt_app_publish_status(new_st);

    httpd_resp_set_status(req, "303 See Other");
    httpd_resp_set_hdr(req, "Location", "/");
    return httpd_resp_send(req, NULL, 0);
}

/**
 * @brief HTTP GET handler для REST API "/api/status"
 */
static esp_err_t http_api_status_handler(httpd_req_t *req)
{
    relay_state_t st = relay_driver_get_state(&s_relay);
    char json_buf[128];
    snprintf(json_buf, sizeof(json_buf),
             "{\"relay_state\":\"%s\",\"gpio\":0,\"active_low\":true}",
             (st == RELAY_STATE_ON) ? "ON" : "OFF");

    httpd_resp_set_type(req, "application/json");
    return httpd_resp_send(req, json_buf, HTTPD_RESP_USE_STRLEN);
}

/**
 * @brief Запуск локального HTTP-вебсервера.
 */
static httpd_handle_t start_webserver(void)
{
    httpd_handle_t server = NULL;
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.stack_size = 4096;

    ESP_LOGI(TAG, "Запуск HTTP-вебсервера на порту: %d", config.server_port);
    if (httpd_start(&server, &config) == ESP_OK) {
        httpd_uri_t uri_root = { .uri = "/", .method = HTTP_GET, .handler = http_root_handler, .user_ctx = NULL };
        httpd_register_uri_handler(server, &uri_root);

        httpd_uri_t uri_on = { .uri = "/on", .method = HTTP_GET, .handler = http_on_handler, .user_ctx = NULL };
        httpd_register_uri_handler(server, &uri_on);

        httpd_uri_t uri_off = { .uri = "/off", .method = HTTP_GET, .handler = http_off_handler, .user_ctx = NULL };
        httpd_register_uri_handler(server, &uri_off);

        httpd_uri_t uri_toggle = { .uri = "/toggle", .method = HTTP_GET, .handler = http_toggle_handler, .user_ctx = NULL };
        httpd_register_uri_handler(server, &uri_toggle);

        httpd_uri_t uri_api = { .uri = "/api/status", .method = HTTP_GET, .handler = http_api_status_handler, .user_ctx = NULL };
        httpd_register_uri_handler(server, &uri_api);

        return server;
    }

    ESP_LOGE(TAG, "Не вдалося запустити HTTP-сервер!");
    return NULL;
}

/**
 * @brief Неблокуюча фонова задача моніторингу стану системи FreeRTOS.
 */
static void system_monitor_task(void *pvParameters)
{
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(10000));
        relay_state_t state = relay_driver_get_state(&s_relay);
        ESP_LOGI(TAG, "[Монітор системи] Стан реле: %s | Вільна оперативна пам'ять Heap: %u байт",
                 (state == RELAY_STATE_ON) ? "ON" : "OFF",
                 (unsigned int)esp_get_free_heap_size());
    }
}

/**
 * @brief Головна точка входу прошивки app_main().
 */
void app_main(void)
{
    ESP_LOGI(TAG, "==================================================");
    ESP_LOGI(TAG, "  ESP-01S Relay Module Firmware (ESP8266 RTOS SDK)");
    ESP_LOGI(TAG, "==================================================");

    /* 1. Ініціалізація енергонезалежної пам'яті NVS (необхідно для Wi-Fi стека) */
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    /* 2. Низькорівнева безпечна ініціалізація драйвера реле (GPIO0) */
    relay_config_t relay_cfg = {
        .gpio_pin = RELAY_DEFAULT_GPIO_PIN,
        .active_low = true, /* ESP-01S Relay module має інверсну логіку (Active LOW) */
        .initial_state = RELAY_STATE_OFF /* Безпечний початковий вимкнений стан */
    };
    ESP_ERROR_CHECK(relay_driver_init(&s_relay, &relay_cfg));

    /* 3. Ініціалізація та запуск мережевого модуля Wi-Fi Station */
    wifi_manager_config_t wifi_cfg = {
        .ssid = "Home_WiFi_Network",
        .password = "SecurePassword123",
        .max_retry = 5
    };
    ESP_ERROR_CHECK(wifi_manager_init(&wifi_cfg));

    /* 4. Очікування успішного з'єднання з Wi-Fi через FreeRTOS Event Group */
    EventGroupHandle_t wifi_events = wifi_manager_get_event_group();
    ESP_LOGI(TAG, "Очікування мережевого підключення Wi-Fi...");
    EventBits_t bits = xEventGroupWaitBits(wifi_events,
                                           WIFI_CONNECTED_BIT | WIFI_FAIL_BIT,
                                           pdFALSE,
                                           pdFALSE,
                                           portMAX_DELAY);

    if (bits & WIFI_CONNECTED_BIT) {
        ESP_LOGI(TAG, "Мережу підключено! Запуск HTTP вебсервера та MQTT клієнта...");

        /* 5. Запуск HTTP-сервера для локального керування через браузер */
        s_web_server = start_webserver();

        /* 6. Налаштування та запуск MQTT-клієнта */
        mqtt_app_config_t mqtt_cfg = {
            .broker_uri = "mqtt://192.168.1.100:1883",
            .client_id = "ESP01S_Relay_Device",
            .username = "",
            .password = "",
            .relay_handle = &s_relay
        };
        mqtt_app_start(&mqtt_cfg);
    } else if (bits & WIFI_FAIL_BIT) {
        ESP_LOGE(TAG, "Не вдалося підключитися до Wi-Fi! Мережеві сервіси недоступні.");
    }

    /* 7. Створення фонової задачи FreeRTOS для моніторингу системи */
    xTaskCreate(system_monitor_task, "sys_monitor", 2048, NULL, 5, NULL);

    ESP_LOGI(TAG, "Основний процес app_main завершено. Сервіси працюють у фонових задачах FreeRTOS.");
}
