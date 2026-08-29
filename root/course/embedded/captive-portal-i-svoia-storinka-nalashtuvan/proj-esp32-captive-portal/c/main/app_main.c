#include <stdbool.h>
#include <stdio.h>
#include <string.h>

#include "config_store.h"
#include "dns_server.h"
#include "esp_event.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_wifi.h"
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "http_server.h"
#include "nvs_flash.h"
#include "wifi_ap.h"

static const char *TAG = "app";

/* SSID точки доступу налаштування. Останні байти MAC роблять його
 * унікальним, коли поруч вмикають кілька однакових пристроїв. */
#define PORTAL_SSID_PREFIX "ESP32-Setup-"

/* Скільки разів пробуємо збережену мережу, перш ніж підняти портал. */
#define STA_MAX_RETRIES 5

/* Скільки чекаємо на адресу від DHCP чужої мережі. */
#define STA_CONNECT_TIMEOUT_MS 20000

#define BIT_STA_GOT_IP BIT0
#define BIT_STA_FAILED BIT1

static EventGroupHandle_t s_sta_events = NULL;
static int s_sta_retries = 0;
static httpd_handle_t s_http_server = NULL;

static void wifi_event_handler(void *arg, esp_event_base_t base,
                               int32_t event_id, void *event_data)
{
    (void)arg;

    if (base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED) {
        const wifi_event_sta_disconnected_t *ev = event_data;

        if (s_sta_retries < STA_MAX_RETRIES) {
            s_sta_retries++;
            ESP_LOGW(TAG, "Розрив зв'язку (причина %d), спроба %d із %d",
                     ev->reason, s_sta_retries, STA_MAX_RETRIES);
            esp_wifi_connect();
        } else {
            ESP_LOGE(TAG, "Збережена мережа недоступна, причина %d", ev->reason);
            xEventGroupSetBits(s_sta_events, BIT_STA_FAILED);
        }
    } else if (base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
        const ip_event_got_ip_t *ev = event_data;
        ESP_LOGI(TAG, "Отримано адресу " IPSTR, IP2STR(&ev->ip_info.ip));
        s_sta_retries = 0;
        xEventGroupSetBits(s_sta_events, BIT_STA_GOT_IP);
    } else if (base == WIFI_EVENT && event_id == WIFI_EVENT_AP_STACONNECTED) {
        const wifi_event_ap_staconnected_t *ev = event_data;
        ESP_LOGI(TAG, "До порталу під'єднався клієнт, aid=%d", ev->aid);
    }
}

/* Ім'я точки доступу з хвостом апаратної адреси: ESP32-Setup-A1B2. */
static void build_portal_ssid(char *out, size_t capacity)
{
    uint8_t mac[6] = {0};
    esp_wifi_get_mac(WIFI_IF_AP, mac);
    snprintf(out, capacity, PORTAL_SSID_PREFIX "%02X%02X", mac[4], mac[5]);
}

static void start_portal(void)
{
    char ssid[33];
    build_portal_ssid(ssid, sizeof(ssid));

    ESP_ERROR_CHECK(wifi_ap_start(ssid, NULL));
    ESP_ERROR_CHECK(dns_server_start(esp_ip4addr_aton(WIFI_AP_IP_ADDR)));
    ESP_ERROR_CHECK(http_server_init(&s_http_server));

    ESP_LOGI(TAG, "Портал налаштування працює: під'єднайтеся до \"%s\"", ssid);
}

/*
 * Повертає true, коли збережена мережа справді піднялася.
 * Помилка тут не фатальна: пристрій просто вертається до порталу,
 * бо пароль домашнього роутера міг змінитися.
 */
static bool try_saved_network(void)
{
    portal_credentials_t creds;
    if (config_store_load(&creds) != ESP_OK) {
        return false;
    }

    ESP_LOGI(TAG, "Пробуємо збережену мережу \"%s\"", creds.ssid);

    if (wifi_sta_connect(creds.ssid, creds.password) != ESP_OK) {
        return false;
    }

    const EventBits_t bits = xEventGroupWaitBits(
        s_sta_events, BIT_STA_GOT_IP | BIT_STA_FAILED,
        pdFALSE, pdFALSE, pdMS_TO_TICKS(STA_CONNECT_TIMEOUT_MS));

    if (bits & BIT_STA_GOT_IP) {
        return true;
    }

    /* Ні адреси, ні остаточної відмови — далі чекати немає сенсу. */
    esp_wifi_disconnect();
    return false;
}

void app_main(void)
{
    esp_err_t err = nvs_flash_init();
    if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        /* Розділ лишився від старішої прошивки або переповнений — чистимо. */
        ESP_ERROR_CHECK(nvs_flash_erase());
        err = nvs_flash_init();
    }
    ESP_ERROR_CHECK(err);

    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());

    s_sta_events = xEventGroupCreate();
    ESP_ERROR_CHECK(s_sta_events != NULL ? ESP_OK : ESP_ERR_NO_MEM);

    ESP_ERROR_CHECK(esp_event_handler_instance_register(
        WIFI_EVENT, ESP_EVENT_ANY_ID, wifi_event_handler, NULL, NULL));
    ESP_ERROR_CHECK(esp_event_handler_instance_register(
        IP_EVENT, IP_EVENT_STA_GOT_IP, wifi_event_handler, NULL, NULL));

    ESP_ERROR_CHECK(wifi_stack_init());

    if (config_store_is_configured() && try_saved_network()) {
        ESP_LOGI(TAG, "Робочий режим: портал не потрібен");
        return;
    }

    /*
     * Або конфігурації немає взагалі (пристрій щойно з конвеєра),
     * або збережена мережа не піднялася. Обидва випадки ведуть в одне
     * місце — до сторінки налаштувань.
     */
    start_portal();
}
