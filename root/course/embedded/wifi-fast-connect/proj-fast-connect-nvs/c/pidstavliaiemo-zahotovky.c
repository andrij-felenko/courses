#include "esp_wifi.h"
#include <string.h>

#define WIFI_SSID "MyNetwork"
#define WIFI_PASS "secret123"

// Зібрати конфіг станції. Якщо st != NULL і має канал — підставляємо підказку.
static void apply_sta_config(const fastconn_t *st)
{
    wifi_config_t cfg = { 0 };
    strncpy((char *)cfg.sta.ssid,     WIFI_SSID, sizeof(cfg.sta.ssid));
    strncpy((char *)cfg.sta.password, WIFI_PASS, sizeof(cfg.sta.password));

    if (st && st->channel >= 1 && st->channel <= 13) {
        cfg.sta.channel = st->channel;   // теплий старт: шукати з відомого каналу
    } else {
        cfg.sta.channel = 0;             // холодний старт: повний скан
    }
    // bssid_set лишаємо 0 — на ESP32 BSSID підключення не прискорює
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &cfg));
}
