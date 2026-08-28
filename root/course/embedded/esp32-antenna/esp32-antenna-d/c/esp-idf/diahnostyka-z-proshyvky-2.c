// Wi-Fi уже піднято в режимі STA (esp_wifi_init / set_mode / start),
// під'єднуватися до точки доступу для скану не треба.
#include "esp_wifi.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "scan";

void scan_task(void *arg) {
    while (1) {
        uint16_t room = 20;                        // скільки записів заберемо
        wifi_ap_record_t recs[20];
        ESP_ERROR_CHECK(esp_wifi_scan_start(NULL, true));   // блокуючий скан усіх каналів
        ESP_ERROR_CHECK(esp_wifi_scan_get_ap_records(&room, recs));

        uint16_t found = 0;
        esp_wifi_scan_get_ap_num(&found);
        ESP_LOGI(TAG, "знайдено мереж: %u", found);

        int strong = 0;                            // скільки з них гучніші за −80 dBm
        for (int i = 0; i < room; i++) {
            if (recs[i].rssi > -80) strong++;
            ESP_LOGI(TAG, "  %-24s  %4d dBm  ch%u",
                     (const char *)recs[i].ssid, recs[i].rssi, recs[i].primary);
        }
        ESP_LOGI(TAG, "з них упевнених (> −80 dBm): %d\n", strong);

        vTaskDelay(pdMS_TO_TICKS(5000));
    }
}
