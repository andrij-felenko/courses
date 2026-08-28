#include "nvs_flash.h"
#include "esp_netif.h"
#include "esp_event.h"
#include "esp_wifi.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "antenna";

void app_main(void) {
    ESP_ERROR_CHECK(nvs_flash_init());          // Wi-Fi тримає калібрування в NVS
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_sta();

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));

    wifi_config_t sta = { .sta = { .ssid = "my-ssid", .password = "my-pass" } };
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &sta));
    ESP_ERROR_CHECK(esp_wifi_start());
    ESP_ERROR_CHECK(esp_wifi_connect());

    while (1) {
        // антенний «стетоскоп»: 10 замірів RSSI з інтервалом,
        // щоб побачити середнє й розкид — рука/метал одразу видно
        wifi_ap_record_t ap;
        int32_t sum = 0;
        int n = 10, got = 0;
        for (int i = 0; i < n; i++) {
            if (esp_wifi_sta_get_ap_info(&ap) == ESP_OK) { sum += ap.rssi; got++; }
            vTaskDelay(pdMS_TO_TICKS(100));
        }
        if (got) ESP_LOGI(TAG, "середній RSSI за %d замірів: %d dBm", got, (int)(sum / got));
        else     ESP_LOGW(TAG, "ще не під'єднано");
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
