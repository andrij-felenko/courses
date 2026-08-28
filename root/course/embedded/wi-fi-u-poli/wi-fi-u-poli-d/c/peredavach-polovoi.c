#include <string.h>
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_sleep.h"
#include "esp_now.h"
#include "nvs_flash.h"

#define FIELD_WIFI_CHANNEL   6
#define SLEEP_INTERVAL_US    (600ULL * 1000ULL * 1000ULL) /* 10 хвилин */

/* MAC-адреса польового базового шлюзу */
static const uint8_t s_gateway_mac[ESP_NOW_ETH_ALEN] = {0x24, 0x6F, 0x28, 0xAA, 0xBB, 0xCC};

/* Структура польового пакета телеметрії */
typedef struct __attribute__((packed)) {
    uint32_t node_id;
    uint32_t message_seq;
    int16_t  temperature_q4; /* Фіксована кома: значення * 16 */
    uint16_t soil_moisture_raw;
    uint16_t battery_mv;
} field_telemetry_t;

static volatile bool s_send_completed = false;
static volatile bool s_send_success = false;

static void espnow_send_cb(const uint8_t *mac_addr, esp_now_send_status_t status) {
    s_send_success = (status == ESP_NOW_SEND_SUCCESS);
    s_send_completed = true;
}

void app_main(void) {
    /* 1. Ініціалізація мінімального стека без створення netif LwIP */
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        nvs_flash_erase();
        nvs_flash_init();
    }

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    esp_wifi_init(&cfg);
    esp_wifi_set_storage(WIFI_STORAGE_RAM); /* Без зайвого зносу Flash */
    esp_wifi_set_mode(WIFI_MODE_STA);
    esp_wifi_start();

    /* 2. Фіксація каналу та далекобійного режиму Long Range PHY */
    esp_wifi_set_channel(FIELD_WIFI_CHANNEL, WIFI_SECOND_CHAN_NONE);
    esp_wifi_set_protocol(WIFI_IF_STA, WIFI_PROTOCOL_11B | WIFI_PROTOCOL_LR);

    /* 3. Ініціалізація ESP-NOW */
    esp_now_init();
    esp_now_register_send_cb(espnow_send_cb);

    esp_now_peer_info_t peer_info = {0};
    memcpy(peer_info.peer_addr, s_gateway_mac, ESP_NOW_ETH_ALEN);
    peer_info.channel = FIELD_WIFI_CHANNEL;
    peer_info.ifidx = WIFI_IF_STA;
    peer_info.encrypt = false;
    esp_now_add_peer(&peer_info);

    /* 4. Підготовка та відправка корисного навантаження */
    field_telemetry_t payload = {
        .node_id = 0x00010042,
        .message_seq = 104,
        .temperature_q4 = 376,       /* 23.5 °C * 16 */
        .soil_moisture_raw = 1840,
        .battery_mv = 3280
    };

    s_send_completed = false;
    esp_now_send(s_gateway_mac, (const uint8_t *)&payload, sizeof(payload));

    /* 5. Очікування апаратного MAC ACK (максимум 15 мс) */
    int timeout_ms = 15;
    while (!s_send_completed && timeout_ms-- > 0) {
        esp_rom_delay_us(1000);
    }

    /* 6. Миттєве вимкнення радіотракту та занурення в глибокий сон */
    esp_wifi_stop();
    esp_wifi_deinit();

    esp_sleep_enable_timer_wakeup(SLEEP_INTERVAL_US);
    esp_deep_sleep_start();
}
