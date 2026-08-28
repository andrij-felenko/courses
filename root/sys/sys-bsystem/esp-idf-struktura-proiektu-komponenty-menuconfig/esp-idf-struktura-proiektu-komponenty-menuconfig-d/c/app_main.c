/* main/app_main.c (C) */
#include <stdio.h>
#include <stdbool.h>
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "sdkconfig.h"

static const char *TAG = "main";

typedef struct {
    const char *ssid;
    uint16_t port;
    bool power_save;
} app_config_t;

void app_main(void) {
    const app_config_t config = {
        .ssid = CONFIG_APP_WIFI_SSID,
        .port = (uint16_t)CONFIG_APP_TELEMETRY_PORT,
#if CONFIG_APP_ENABLE_POWER_SAVE
        .power_save = true,
#else
        .power_save = false,
#endif
    };

    ESP_LOGI(TAG, "Ініціалізація системи...");
    ESP_LOGI(TAG, "SSID: %s, Порт: %u, Енергозбереження: %s",
             config.ssid, config.port, config.power_save ? "УВІМКНЕНО" : "ВИМКНЕНО");

    while (true) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
