#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "esp_netif.h"

#include "app_camera.h"
#include "http_stream_server.h"

#define EXAMPLE_ESP_WIFI_SSID      "ESP32-CAM-Stream"
#define EXAMPLE_ESP_WIFI_PASS      "12345678"
#define EXAMPLE_ESP_MAX_STA_CONN   4

static const char *TAG = "main";

static void wifi_event_handler(void *arg, esp_event_base_t event_base,
                               int32_t event_id, void *event_data) {
    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_AP_STACONNECTED) {
        wifi_event_ap_staconnected_t *event = (wifi_event_ap_staconnected_t *)event_data;
        ESP_LOGI(TAG, "Клієнт підключився: MAC=" MACSTR ", AID=%d",
                 MAC2STR(event->mac), event->aid);
    } else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_AP_STADISCONNECTED) {
        wifi_event_ap_stadisconnected_t *event = (wifi_event_ap_stadisconnected_t *)event_data;
        ESP_LOGI(TAG, "Клієнт відключився: MAC=" MACSTR ", AID=%d",
                 MAC2STR(event->mac), event->aid);
    }
}

static void wifi_init_softap(void) {
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_ap();

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));

    ESP_ERROR_CHECK(esp_event_handler_instance_register(WIFI_EVENT,
                                                        ESP_EVENT_ANY_ID,
                                                        &wifi_event_handler,
                                                        NULL,
                                                        NULL));

    wifi_config_t wifi_config = {
        .ap = {
            .ssid = EXAMPLE_ESP_WIFI_SSID,
            .ssid_len = strlen(EXAMPLE_ESP_WIFI_SSID),
            .channel = 1,
            .password = EXAMPLE_ESP_WIFI_PASS,
            .max_connection = EXAMPLE_ESP_MAX_STA_CONN,
            .authmode = WIFI_AUTH_WPA_WPA2_PSK
        },
    };

    if (strlen(EXAMPLE_ESP_WIFI_PASS) == 0) {
        wifi_config.ap.authmode = WIFI_AUTH_OPEN;
    }

    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_AP));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_AP, &wifi_config));
    ESP_ERROR_CHECK(esp_wifi_start());

    ESP_LOGI(TAG, "Wi-Fi SoftAP ініціалізовано. SSID: %s, пароль: %s",
             EXAMPLE_ESP_WIFI_SSID, EXAMPLE_ESP_WIFI_PASS);
}

void app_main(void) {
    ESP_LOGI(TAG, "Старт системи захоплення та трансляції відео OV2640");

    /* Ініціалізація енергонезалежної пам'яті NVS */
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    /* Ініціалізація Wi-Fi у режимі точки доступу (SoftAP) */
    wifi_init_softap();

    /* Ініціалізація сенсора камери OV2640 */
    ret = app_camera_init(FRAMESIZE_VGA, PIXFORMAT_JPEG);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Критична помилка: Не вдалося ініціалізувати камеру OV2640!");
        return;
    }

    /* Запуск веб-сервера MJPEG-трансляції */
    ret = http_stream_server_start();
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Критична помилка: Не вдалося запустити HTTP-сервер!");
        return;
    }

    ESP_LOGI(TAG, "==================================================");
    ESP_LOGI(TAG, " Потокова трансляція готова!");
    ESP_LOGI(TAG, " Підключайтесь до Wi-Fi: %s", EXAMPLE_ESP_WIFI_SSID);
    ESP_LOGI(TAG, " Відкрийте у браузері: http://192.168.4.1/stream");
    ESP_LOGI(TAG, "==================================================");

    /* Моніторингова задача стану системи */
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(10000));
        ESP_LOGI(TAG, "Стан системи: Вільна SRAM = %lu байт, Вільна PSRAM = %lu байт",
                 (unsigned long)esp_get_free_internal_heap_size(),
                 (unsigned long)heap_caps_get_free_size(MALLOC_CAP_SPIRAM));
    }
}
