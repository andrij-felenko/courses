/**
 * @file net_relay.c
 * @brief Реалізація бездротових інтерфейсів (Wi-Fi/BLE) та ретрансляція даних між ними й нативним USB-портом.
 *
 * Модуль створює Wi-Fi точку доступу (SoftAP), запускає сокет-сервер для прийому мережевих пакетів
 * та реалізує двосторонній прозорий міст (ретранслятор) даних між бездротовими клієнтами та USB CDC.
 */

#include <stdio.h>
#include <string.h>
#include <sys/param.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "lwip/err.h"
#include "lwip/sockets.h"

static const char *TAG = "NET_RELAY";

#define WIFI_AP_SSID      "ESP32-S3-Zero-Relay"
#define WIFI_AP_PASS      "12345678"
#define RELAY_PORT        8888
#define RELAY_BUF_SIZE    1024

// Зовнішній інтерфейс модуля USB CDC та WS2812B
int usb_cdc_read(uint8_t *buf, size_t max_len, TickType_t timeout_ticks);
int usb_cdc_write(const uint8_t *buf, size_t len, TickType_t timeout_ticks);

typedef enum {
    WS2812_STATUS_BOOT = 0,
    WS2812_STATUS_IDLE,
    WS2812_STATUS_DATA_TX_RX,
    WS2812_STATUS_WIRELESS_ACTIVE,
    WS2812_STATUS_ERROR
} ws2812_status_t;

esp_err_t ws2812_set_status(ws2812_status_t status);

static bool s_client_connected = false;
static int s_active_socket = -1;

/**
 * @brief Обробник подій Wi-Fi та мережевого стеку
 */
static void wifi_event_handler(void* arg, esp_event_base_t event_base,
                               int32_t event_id, void* event_data)
{
    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_AP_STACONNECTED) {
        wifi_event_ap_staconnected_t* event = (wifi_event_ap_staconnected_t*) event_data;
        ESP_LOGI(TAG, "Мережевий клієнт підключився (MAC: "MACSTR", AID=%d)",
                 MAC2STR(event->mac), event->aid);
        s_client_connected = true;
        ws2812_set_status(WS2812_STATUS_WIRELESS_ACTIVE);
    } else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_AP_STADISCONNECTED) {
        wifi_event_ap_stadisconnected_t* event = (wifi_event_ap_stadisconnected_t*) event_data;
        ESP_LOGI(TAG, "Мережевий клієнт відключився (MAC: "MACSTR", AID=%d)",
                 MAC2STR(event->mac), event->aid);
        s_client_connected = false;
        ws2812_set_status(WS2812_STATUS_IDLE);
    }
}

/**
 * @brief Ініціалізація Wi-Fi режиму Точки Доступу (SoftAP)
 */
esp_err_t net_relay_init(void)
{
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_ap();

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));

    ESP_ERROR_CHECK(esp_event_handler_instance_register(WIFI_EVENT,
                                                        ESP_EVENT_ANY_ID,
                                                        &wifi_event_handler,
                                                        NULL,
                                                        NULL));

    wifi_config_t wifi_config = {
        .ap = {
            .ssid = WIFI_AP_SSID,
            .ssid_len = strlen(WIFI_AP_SSID),
            .channel = 1,
            .password = WIFI_AP_PASS,
            .max_connection = 4,
            .authmode = WIFI_AUTH_WPA_WPA2_PSK
        },
    };

    if (strlen(WIFI_AP_PASS) == 0) {
        wifi_config.ap.authmode = WIFI_AUTH_OPEN;
    }

    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_AP));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_AP, &wifi_config));
    ESP_ERROR_CHECK(esp_wifi_start());

    ESP_LOGI(TAG, "Wi-Fi SoftAP запущено. SSID: '%s', Порт сокета: %d", WIFI_AP_SSID, RELAY_PORT);
    return ESP_OK;
}

/**
 * @brief Перевірка активності клієнтського бездротового з'єднання
 */
bool net_relay_is_client_connected(void)
{
    return s_client_connected;
}

/**
 * @brief Задача FreeRTOS для ретрансляції даних у двох напрямках (USB CDC <-> Socket Net)
 */
void net_relay_task(void *pvParameters)
{
    char rx_buffer[RELAY_BUF_SIZE];
    uint8_t usb_buffer[RELAY_BUF_SIZE];

    int listen_sock = socket(AF_INET, SOCK_STREAM, IPPROTO_IP);
    if (listen_sock < 0) {
        ESP_LOGE(TAG, "Не вдалося створити сокет: errno %d", errno);
        vTaskDelete(NULL);
        return;
    }

    int opt = 1;
    setsockopt(listen_sock, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in dest_addr;
    dest_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(RELAY_PORT);

    int err = bind(listen_sock, (struct sockaddr *)&dest_addr, sizeof(dest_addr));
    if (err != 0) {
        ESP_LOGE(TAG, "Помилка прив'язки сокета bind: errno %d", errno);
        close(listen_sock);
        vTaskDelete(NULL);
        return;
    }

    err = listen(listen_sock, 1);
    if (err != 0) {
        ESP_LOGE(TAG, "Помилка прослуховування listen: errno %d", errno);
        close(listen_sock);
        vTaskDelete(NULL);
        return;
    }

    ESP_LOGI(TAG, "Сервер ретрансляції готовий та очікує TCP підключення на порту %d...", RELAY_PORT);

    while (1) {
        struct sockaddr_in source_addr;
        socklen_t addr_len = sizeof(source_addr);
        int sock = accept(listen_sock, (struct sockaddr *)&source_addr, &addr_len);
        if (sock < 0) {
            ESP_LOGE(TAG, "Не вдалося прийняти підключення accept: errno %d", errno);
            break;
        }

        // Встановлюємо неблокувальний режим сокета для одночасного опитування USB та сокета
        int flags = fcntl(sock, F_GETFL, 0);
        fcntl(sock, F_SETFL, flags | O_NONBLOCK);

        s_active_socket = sock;
        s_client_connected = true;
        ESP_LOGI(TAG, "TCP клієнт успішно підключився до ретранслятора");
        ws2812_set_status(WS2812_STATUS_WIRELESS_ACTIVE);

        while (1) {
            bool activity = false;

            // 1. Прийом пакетів з мережевого сокета -> Передача в USB CDC
            int len = recv(sock, rx_buffer, sizeof(rx_buffer) - 1, 0);
            if (len > 0) {
                activity = true;
                ESP_LOGI(TAG, "Отримано %d байт з мережі -> відправка в USB", len);
                usb_cdc_write((const uint8_t *)rx_buffer, len, pdMS_TO_TICKS(100));
            } else if (len == 0 || (len < 0 && errno != EWOULDBLOCK && errno != EAGAIN)) {
                ESP_LOGW(TAG, "Мережевий сокет закритий або розірваний");
                break;
            }

            // 2. Прийом пакетів з USB CDC -> Передача в мережевий сокет
            int usb_len = usb_cdc_read(usb_buffer, sizeof(usb_buffer), pdMS_TO_TICKS(10));
            if (usb_len > 0) {
                activity = true;
                ESP_LOGI(TAG, "Отримано %d байт з USB -> відправка в мережу", usb_len);
                int sent = send(sock, usb_buffer, usb_len, 0);
                if (sent < 0 && errno != EWOULDBLOCK && errno != EAGAIN) {
                    ESP_LOGE(TAG, "Помилка відправки в мережевий сокет: errno %d", errno);
                    break;
                }
            }

            // Індикація активного обміну даними на світлодіоді WS2812B
            if (activity) {
                ws2812_set_status(WS2812_STATUS_DATA_TX_RX);
            }

            // Невелика затримка для збереження ресурсів процесора
            vTaskDelay(pdMS_TO_TICKS(10));
        }

        close(sock);
        s_active_socket = -1;
        s_client_connected = false;
        ws2812_set_status(WS2812_STATUS_IDLE);
        ESP_LOGI(TAG, "Сесію сокета завершено. Перехід у стан очікування");
    }

    close(listen_sock);
    vTaskDelete(NULL);
}
