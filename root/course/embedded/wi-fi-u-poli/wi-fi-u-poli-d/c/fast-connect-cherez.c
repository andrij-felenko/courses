#include <string.h>
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_sleep.h"
#include "esp_netif.h"
#include "nvs_flash.h"
#include "lwip/sockets.h"

#define FIELD_SSID          "Farm_Field_Mesh"
#define FIELD_PASSWORD      "FieldSecureKey2026"
#define SLEEP_INTERVAL_US   (300ULL * 1000ULL * 1000ULL) /* 5 хвилин */

/* Структура збереження контексту в RTC Slow Memory (переживає Deep-Sleep) */
typedef struct {
    uint32_t crc32;
    uint8_t  bssid[6];
    uint8_t  channel;
    bool     valid;
    esp_netif_ip_info_t ip_info;
} rtc_wifi_cache_t;

RTC_DATA_ATTR static rtc_wifi_cache_t s_rtc_cache;

static uint32_t calculate_cache_crc(const rtc_wifi_cache_t *cache) {
    const uint8_t *data = (const uint8_t *)&cache->bssid;
    size_t len = sizeof(rtc_wifi_cache_t) - offsetof(rtc_wifi_cache_t, bssid);
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320 & (-(crc & 1)));
        }
    }
    return ~crc;
}

void app_main(void) {
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        nvs_flash_erase();
        nvs_flash_init();
    }

    esp_netif_init();
    esp_event_loop_create_default();
    esp_netif_t *sta_netif = esp_netif_create_default_wifi_sta();

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    esp_wifi_init(&cfg);
    esp_wifi_set_storage(WIFI_STORAGE_RAM);
    esp_wifi_set_mode(WIFI_MODE_STA);

    wifi_config_t wifi_cfg = {0};
    strncpy((char *)wifi_cfg.sta.ssid, FIELD_SSID, sizeof(wifi_cfg.sta.ssid));
    strncpy((char *)wifi_cfg.sta.password, FIELD_PASSWORD, sizeof(wifi_cfg.sta.password));

    bool is_fast_connect = false;
    if (esp_reset_reason() == ESP_RST_DEEPSLEEP && s_rtc_cache.valid) {
        uint32_t calculated_crc = calculate_cache_crc(&s_rtc_cache);
        if (calculated_crc == s_rtc_cache.crc32) {
            /* 1. Швидкий старт: фіксація каналу та BSSID */
            wifi_cfg.sta.channel = s_rtc_cache.channel;
            memcpy(wifi_cfg.sta.bssid, s_rtc_cache.bssid, 6);
            wifi_cfg.sta.bssid_set = 1;

            /* 2. Статична IP-конфігурація без виклику DHCP */
            esp_netif_dhcpc_stop(sta_netif);
            esp_netif_set_ip_info(sta_netif, &s_rtc_cache.ip_info);

            is_fast_connect = true;
        }
    }

    esp_wifi_set_config(WIFI_IF_STA, &wifi_cfg);
    esp_wifi_start();
    esp_wifi_connect();

    /* 3. Очікування зв'язку (у режимі Fast Connect займає < 80 мс) */
    wifi_ap_record_t ap_info;
    int wait_limit = is_fast_connect ? 100 : 400; /* ітерацій по 10 мс */
    bool connected = false;

    while (wait_limit-- > 0) {
        if (esp_wifi_sta_get_ap_info(&ap_info) == ESP_OK) {
            connected = true;
            break;
        }
        vTaskDelay(pdMS_TO_TICKS(10));
    }

    if (connected && !is_fast_connect) {
        /* Перший холодний старт: збереження параметрів у RTC */
        s_rtc_cache.channel = ap_info.primary;
        memcpy(s_rtc_cache.bssid, ap_info.bssid, 6);
        esp_netif_get_ip_info(sta_netif, &s_rtc_cache.ip_info);
        s_rtc_cache.valid = true;
        s_rtc_cache.crc32 = calculate_cache_crc(&s_rtc_cache);
    }

    /* 4. Відправка UDP-телеметрії */
    if (connected) {
        int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_IP);
        if (sock >= 0) {
            struct sockaddr_in dest_addr = {
                .sin_addr.s_addr = inet_addr("192.168.1.1"),
                .sin_family = AF_INET,
                .sin_port = htons(5005)
            };
            const char telemetry[] = "{\"node\":104,\"v_bat\":3.28,\"temp\":23.5}";
            sendto(sock, telemetry, strlen(telemetry), 0, (struct sockaddr *)&dest_addr, sizeof(dest_addr));
            close(sock);
        }
    }

    /* 5. Зупинка Wi-Fi та Deep-Sleep */
    esp_wifi_stop();
    esp_sleep_enable_timer_wakeup(SLEEP_INTERVAL_US);
    esp_deep_sleep_start();
}
