#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"

#define TAG "ROAM_MGR"

#define ROAM_RSSI_THRESHOLD_DBM   (-75)  /* Поріг активації пошуку нової AP */
#define ROAM_HYSTERESIS_MARGIN_DB (6)    /* Обов'язковий запас сигналу кандидата */
#define ROAM_EWMA_ALPHA_PERCENT   (20)   /* Коефіцієнт згладжування 0.2 (20%) */
#define ROAM_HOLDOFF_PERIOD_MS    (5000) /* Мінімальний інтервал між переходами */
#define ROAM_POLL_INTERVAL_MS     (1000) /* Інтервал опитування RSSI */

typedef enum {
    ROAM_STATE_INIT,
    ROAM_STATE_CONNECTED,
    ROAM_STATE_SCANNING,
    ROAM_STATE_HANDOVER
} roam_state_t;

typedef struct {
    roam_state_t state;
    char target_ssid[33];
    uint8_t current_bssid[6];
    uint8_t current_channel;
    int8_t current_rssi_filtered;
    int64_t last_handover_timestamp_us;
} roam_manager_t;

static roam_manager_t s_mgr;

static void update_rssi_filter(int8_t raw_rssi) {
    if (s_mgr.current_rssi_filtered == 0) {
        s_mgr.current_rssi_filtered = raw_rssi;
    } else {
        /* EWMA: RSSI[k] = α · Raw + (1 - α) · RSSI[k-1] у цілочисельній арифметиці */
        int32_t weighted = (raw_rssi * ROAM_EWMA_ALPHA_PERCENT) + 
                           (s_mgr.current_rssi_filtered * (100 - ROAM_EWMA_ALPHA_PERCENT));
        s_mgr.current_rssi_filtered = (int8_t)(weighted / 100);
    }
}

static void evaluate_scan_results_and_roam(void) {
    uint16_t ap_count = 0;
    esp_wifi_scan_get_ap_num(&ap_count);
    if (ap_count == 0) {
        s_mgr.state = ROAM_STATE_CONNECTED;
        return;
    }

    wifi_ap_record_t *records = (wifi_ap_record_t *)malloc(sizeof(wifi_ap_record_t) * ap_count);
    if (!records) {
        s_mgr.state = ROAM_STATE_CONNECTED;
        return;
    }

    if (esp_wifi_scan_get_ap_records(&ap_count, records) != ESP_OK) {
        free(records);
        s_mgr.state = ROAM_STATE_CONNECTED;
        return;
    }

    int8_t best_score = -127;
    uint8_t best_bssid[6] = {0};
    uint8_t best_channel = 0;
    bool candidate_found = false;

    const int8_t required_rssi = s_mgr.current_rssi_filtered + ROAM_HYSTERESIS_MARGIN_DB;

    for (int i = 0; i < ap_count; ++i) {
        /* Перевірка відповідності імені мережі */
        if (strcmp((const char *)records[i].ssid, s_mgr.target_ssid) != 0) {
            continue;
        }
        /* Ігнорування поточної точки доступу */
        if (memcmp(records[i].bssid, s_mgr.current_bssid, 6) == 0) {
            continue;
        }

        /* Перевірка порогу гістерезису */
        if (records[i].rssi >= required_rssi) {
            int8_t score = records[i].rssi;
            if (records[i].primary > 14) {
                score += 10; /* Бонус за діапазон 5 ГГц */
            }

            if (score > best_score) {
                best_score = score;
                memcpy(best_bssid, records[i].bssid, 6);
                best_channel = records[i].primary;
                candidate_found = true;
            }
        }
    }

    free(records);

    if (candidate_found) {
        int64_t now_us = esp_timer_get_time();
        if ((now_us - s_mgr.last_handover_timestamp_us) < (ROAM_HOLDOFF_PERIOD_MS * 1000LL)) {
            ESP_LOGW(TAG, "Кандидат знайдений, але таймер затримки ще активний. Перехід скасовано.");
            s_mgr.state = ROAM_STATE_CONNECTED;
            return;
        }

        ESP_LOGI(TAG, "Ініціація хендоверу на BSSID %02x:%02x:%02x:%02x:%02x:%02x (Канал %d, RSSI %d dBm)",
                 best_bssid[0], best_bssid[1], best_bssid[2],
                 best_bssid[3], best_bssid[4], best_bssid[5], best_channel, best_score);

        s_mgr.state = ROAM_STATE_HANDOVER;
        s_mgr.last_handover_timestamp_us = now_us;

        wifi_config_t wifi_cfg;
        esp_wifi_get_config(WIFI_IF_STA, &wifi_cfg);
        wifi_cfg.sta.bssid_set = 1;
        memcpy(wifi_cfg.sta.bssid, best_bssid, 6);
        wifi_cfg.sta.channel = best_channel;

        esp_wifi_set_config(WIFI_IF_STA, &wifi_cfg);
        esp_wifi_disconnect();
        esp_wifi_connect();
    } else {
        s_mgr.state = ROAM_STATE_CONNECTED;
    }
}

static void roam_monitor_task(void *arg) {
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(ROAM_POLL_INTERVAL_MS));

        if (s_mgr.state != ROAM_STATE_CONNECTED) {
            continue;
        }

        wifi_ap_record_t ap_info;
        if (esp_wifi_sta_get_ap_info(&ap_info) == ESP_OK) {
            memcpy(s_mgr.current_bssid, ap_info.bssid, 6);
            s_mgr.current_channel = ap_info.primary;
            update_rssi_filter(ap_info.rssi);

            ESP_LOGD(TAG, "Моніторинг: Сирий RSSI = %d dBm, Згладжений = %d dBm",
                     ap_info.rssi, s_mgr.current_rssi_filtered);

            if (s_mgr.current_rssi_filtered < ROAM_RSSI_THRESHOLD_DBM) {
                ESP_LOGI(TAG, "Сигнал нижче порогу (%d dBm). Старт неблокувального сканування...",
                         s_mgr.current_rssi_filtered);
                s_mgr.state = ROAM_STATE_SCANNING;

                wifi_scan_config_t scan_cfg = {
                    .ssid = (uint8_t *)s_mgr.target_ssid,
                    .bssid = NULL,
                    .channel = 0,
                    .show_hidden = false,
                    .scan_type = WIFI_SCAN_TYPE_ACTIVE,
                    .scan_time.active.min = 15,
                    .scan_time.active.max = 30
                };
                esp_wifi_scan_start(&scan_cfg, false);
            }
        }
    }
}

static void wifi_event_handler(void *arg, esp_event_base_t event_base,
                               int32_t event_id, void *event_data) {
    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_SCAN_DONE) {
        if (s_mgr.state == ROAM_STATE_SCANNING) {
            evaluate_scan_results_and_roam();
        }
    } else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_CONNECTED) {
        wifi_event_sta_connected_t *evt = (wifi_event_sta_connected_t *)event_data;
        memcpy(s_mgr.current_bssid, evt->bssid, 6);
        s_mgr.current_channel = evt->channel;
        s_mgr.state = ROAM_STATE_CONNECTED;
        ESP_LOGI(TAG, "З'єднання встановлено з BSSID: %02x:%02x:%02x:%02x:%02x:%02x на каналі %d",
                 evt->bssid[0], evt->bssid[1], evt->bssid[2],
                 evt->bssid[3], evt->bssid[4], evt->bssid[5], evt->channel);
    } else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED) {
        s_mgr.state = ROAM_STATE_INIT;
        s_mgr.current_rssi_filtered = 0;
        esp_wifi_connect();
    }
}

void roam_manager_start(const char *ssid) {
    memset(&s_mgr, 0, sizeof(s_mgr));
    strncpy(s_mgr.target_ssid, ssid, sizeof(s_mgr.target_ssid) - 1);
    s_mgr.state = ROAM_STATE_INIT;

    esp_event_handler_instance_register(WIFI_EVENT, ESP_EVENT_ANY_ID,
                                        &wifi_event_handler, NULL, NULL);
    xTaskCreate(roam_monitor_task, "roam_monitor", 4096, NULL, 5, NULL);
}
