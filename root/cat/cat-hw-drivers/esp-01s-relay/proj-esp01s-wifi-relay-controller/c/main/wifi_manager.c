#include "wifi_manager.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "nvs_flash.h"
#include <string.h>

static const char *TAG = "WIFI_MANAGER";

static EventGroupHandle_t s_wifi_event_group = NULL;
static int s_retry_num = 0;
static uint8_t s_max_retry_limit = 10;
static bool s_is_connected = false;

/**
 * @brief Обробник подій Wi-Fi та IP-стека.
 */
static void wifi_event_handler(void* arg, esp_event_base_t event_base,
                               int32_t event_id, void* event_data)
{
    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_START) {
        ESP_LOGI(TAG, "Запуск Wi-Fi Station, спроба підключення...");
        esp_wifi_connect();
    } else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED) {
        s_is_connected = false;
        if (s_retry_num < s_max_retry_limit) {
            esp_wifi_connect();
            s_retry_num++;
            ESP_LOGW(TAG, "Втрачено Wi-Fi з'єднання. Спроба перепідключення (%d/%d)...",
                     s_retry_num, s_max_retry_limit);
        } else {
            xEventGroupSetBits(s_wifi_event_group, WIFI_FAIL_BIT);
            ESP_LOGE(TAG, "Не вдалося підключитися до Wi-Fi після %d спроб", s_max_retry_limit);
        }
        xEventGroupClearBits(s_wifi_event_group, WIFI_CONNECTED_BIT);
    } else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
        ip_event_got_ip_t* event = (ip_event_got_ip_t*) event_data;
        ESP_LOGI(TAG, "Wi-Fi підключено! Отримано IP-адресу: " IPSTR, IP2STR(&event->ip_info.ip));
        s_retry_num = 0;
        s_is_connected = true;
        xEventGroupSetBits(s_wifi_event_group, WIFI_CONNECTED_BIT);
    }
}

esp_err_t wifi_manager_init(const wifi_manager_config_t *config)
{
    if (config == NULL || strlen(config->ssid) == 0) {
        ESP_LOGE(TAG, "Недійсні конфігураційні дані Wi-Fi");
        return ESP_ERR_INVALID_ARG;
    }

    s_max_retry_limit = (config->max_retry > 0) ? config->max_retry : 10;

    /* Створення FreeRTOS Event Group для сигналізації про стан мережі */
    s_wifi_event_group = xEventGroupCreate();
    if (s_wifi_event_group == NULL) {
        ESP_LOGE(TAG, "Не вдалося створити Event Group Wi-Fi");
        return ESP_ERR_NO_MEM;
    }

    /* Ініціалізація мережевого інтерфейсу TCP/IP */
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_sta();

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));

    /* Реєстрація обробників подій для Wi-Fi та IP */
    ESP_ERROR_CHECK(esp_event_handler_instance_register(WIFI_EVENT,
                                                        ESP_EVENT_ANY_ID,
                                                        &wifi_event_handler,
                                                        NULL,
                                                        NULL));
    ESP_ERROR_CHECK(esp_event_handler_instance_register(IP_EVENT,
                                                        IP_EVENT_STA_GOT_IP,
                                                        &wifi_event_handler,
                                                        NULL,
                                                        NULL));

    wifi_config_t wifi_config = {0};
    strncpy((char *)wifi_config.sta.ssid, config->ssid, sizeof(wifi_config.sta.ssid) - 1);
    strncpy((char *)wifi_config.sta.password, config->password, sizeof(wifi_config.sta.password) - 1);
    wifi_config.sta.threshold.authmode = WIFI_AUTH_WPA2_PSK;

    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_config));
    ESP_ERROR_CHECK(esp_wifi_start());

    ESP_LOGI(TAG, "Модуль Wi-Fi успішно ініціалізовано. SSID: %s", config->ssid);

    return ESP_OK;
}

EventGroupHandle_t wifi_manager_get_event_group(void)
{
    return s_wifi_event_group;
}

bool wifi_manager_is_connected(void)
{
    return s_is_connected;
}

esp_err_t wifi_manager_stop(void)
{
    if (s_wifi_event_group != NULL) {
        esp_wifi_stop();
        esp_wifi_deinit();
        vEventGroupDelete(s_wifi_event_group);
        s_wifi_event_group = NULL;
        s_is_connected = false;
        ESP_LOGI(TAG, "Wi-Fi стек зупинено");
    }
    return ESP_OK;
}
