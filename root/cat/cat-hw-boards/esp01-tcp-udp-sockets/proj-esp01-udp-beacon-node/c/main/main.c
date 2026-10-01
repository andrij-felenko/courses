/**
 * @file main.c
 * @brief Головний модуль прошивки ESP-IDF для демонстрації роботи з UDP-сокетом на ESP-01.
 */

#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "nvs_flash.h"

#include "udp_broadcast.h"

#define WIFI_SSID      "ESP01_AP"
#define WIFI_PASS      "12345678"

static const char *TAG = "MAIN_APP";

/**
 * @brief Завдання FreeRTOS для обробки неблокуючого UDP-сокета
 */
static void udp_server_task(void *pvParameters)
{
    ESP_LOGI(TAG, "Запуск завдання UDP-сокета...");

    int sock_fd = udp_socket_create();
    if (sock_fd < 0) {
        ESP_LOGE(TAG, "Неможливо продовжити: сокет не створено.");
        vTaskDelete(NULL);
        return;
    }

    uint8_t rx_buffer[RX_BUFFER_SIZE];
    telemetry_pkt_t tx_pkt;
    uint32_t seq_counter = 0;
    TickType_t last_broadcast_time = xTaskGetTickCount();

    while (1) {
        // 1. Опитування вхідних датаграм у неблокуючому режимі
        int len = udp_socket_receive(sock_fd, rx_buffer, sizeof(rx_buffer));
        if (len > 0) {
            ESP_LOGI(TAG, "Вміст вхідного пакета: %s", (char *)rx_buffer);
        } else if (len < 0) {
            ESP_LOGE(TAG, "Критична помилка сокета. Перезапуск з'єднання...");
            udp_socket_close(&sock_fd);
            vTaskDelay(pdMS_TO_TICKS(2000));
            sock_fd = udp_socket_create();
        }

        // 2. Періодична відправка широкомовного маяка кожні 2 секунди
        if ((xTaskGetTickCount() - last_broadcast_time) >= pdMS_TO_TICKS(2000)) {
            last_broadcast_time = xTaskGetTickCount();

            memset(&tx_pkt, 0, sizeof(tx_pkt));
            tx_pkt.device_id = 0xESP01;
            tx_pkt.sequence = ++seq_counter;
            tx_pkt.uptime_ms = xTaskGetTickCount() * portTICK_PERIOD_MS;
            snprintf(tx_pkt.data, sizeof(tx_pkt.data), "ESP-01 UDP Beacon #%u", (unsigned int)seq_counter);
            tx_pkt.payload_len = strlen(tx_pkt.data);

            udp_socket_send_broadcast(sock_fd, &tx_pkt);
        }

        // Невелика затримка (50 мс) для запобігання перевантаженню процесора у циклі
        vTaskDelay(pdMS_TO_TICKS(50));
    }

    // Очищення ресурсів при виході із циклу
    udp_socket_close(&sock_fd);
    vTaskDelete(NULL);
}

/**
 * @brief Проста ініціалізація Wi-Fi у режимі Точки Доступу (SoftAP)
 */
static void wifi_init_softap(void)
{
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_ap();

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));

    wifi_config_t wifi_config = {
        .ap = {
            .ssid = WIFI_SSID,
            .ssid_len = strlen(WIFI_SSID),
            .channel = 1,
            .password = WIFI_PASS,
            .max_connection = 4,
            .authmode = WIFI_AUTH_WPA_WPA2_PSK
        },
    };

    if (strlen(WIFI_PASS) == 0) {
        wifi_config.ap.authmode = WIFI_AUTH_OPEN;
    }

    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_AP));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_AP, &wifi_config));
    ESP_ERROR_CHECK(esp_wifi_start());

    ESP_LOGI(TAG, "Wi-Fi SoftAP ініціалізовано. SSID: %s, Канал: %d", WIFI_SSID, 1);
}

/**
 * @brief Точка входу в програму ESP-IDF
 */
void app_main(void)
{
    // Ініціалізація енергонезалежної пам'яті NVS
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    ESP_LOGI(TAG, "Запуск системного модуля ESP-01 UDP Socket...");

    // 1. Старт мережевого Wi-Fi стека
    wifi_init_softap();

    // 2. Створення завдання FreeRTOS для обробки сокета
    xTaskCreate(udp_server_task, "udp_server_task", 4096, NULL, 5, NULL);
}
