#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "esp_psram.h"
#include "esp_heap_caps.h"

#include "ov2640_driver.h"
#include "mjpeg_server.h"

static const char *TAG = "app_main";

#define EXAMPLE_ESP_WIFI_SSID      "ESP32-CAM-AP"
#define EXAMPLE_ESP_WIFI_PASS      "12345678"
#define EXAMPLE_MAX_STA_CONN       4

/* Прив'язка пинів для модуля ESP32-CAM (AI-Thinker OV2640) */
#define CAM_PIN_PWDN    32
#define CAM_PIN_RESET   -1
#define CAM_PIN_XCLK     0
#define CAM_PIN_SIOD    26
#define CAM_PIN_SIOC    27

#define CAM_PIN_D7      35
#define CAM_PIN_D6      34
#define CAM_PIN_D5      39
#define CAM_PIN_D4      36
#define CAM_PIN_D3      21
#define CAM_PIN_D2      19
#define CAM_PIN_D1      18
#define CAM_PIN_D0       5
#define CAM_PIN_VSYNC   25
#define CAM_PIN_HREF    23
#define CAM_PIN_PCLK    22

static void wifi_event_handler(void* arg, esp_event_base_t event_base,
                               int32_t event_id, void* event_data) {
    if (event_id == WIFI_EVENT_AP_STACONNECTED) {
        wifi_event_ap_staconnected_t* event = (wifi_event_ap_staconnected_t*) event_data;
        ESP_LOGI(TAG, "Новий клієнт підключився: MAC=" MACSTR ", AID=%d",
                 MAC2STR(event->mac), event->aid);
    } else if (event_id == WIFI_EVENT_AP_STADISCONNECTED) {
        wifi_event_ap_stadisconnected_t* event = (wifi_event_ap_stadisconnected_t*) event_data;
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
            .max_connection = EXAMPLE_MAX_STA_CONN,
            .authmode = WIFI_AUTH_WPA_WPA2_PSK
        },
    };

    if (strlen(EXAMPLE_ESP_WIFI_PASS) == 0) {
        wifi_config.ap.authmode = WIFI_AUTH_OPEN;
    }

    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_AP));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_AP, &wifi_config));
    ESP_ERROR_CHECK(esp_wifi_start());

    ESP_LOGI(TAG, "Wi-Fi Access Point запущено. SSID: %s, пароль: %s",
             EXAMPLE_ESP_WIFI_SSID, EXAMPLE_ESP_WIFI_PASS);
}

static void system_monitor_task(void *pvParameters) {
    (void)pvParameters;
    while (1) {
        size_t free_sram = heap_caps_get_free_size(MALLOC_CAP_INTERNAL);
        size_t free_psram = heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
        size_t min_sram = heap_caps_get_minimum_free_size(MALLOC_CAP_INTERNAL);

        ESP_LOGI(TAG, "[Монітор] Внутрішня SRAM: %u байт (мін: %u) | Зовнішня PSRAM: %u байт",
                 (unsigned int)free_sram, (unsigned int)min_sram, (unsigned int)free_psram);

        vTaskDelay(pdMS_TO_TICKS(5000));
    }
}

void app_main(void) {
    ESP_LOGI(TAG, "=== Запуск системи відеоспостереження ESP32 OV2640 ===");

    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    size_t psram_size = heap_caps_get_total_size(MALLOC_CAP_SPIRAM);
    if (psram_size == 0) {
        ESP_LOGE(TAG, "КРИТИЧНА ПОМИЛКА: Пам'ять PSRAM не виявлена! Робота з DVP буферами вимагає PSRAM.");
        return;
    }
    ESP_LOGI(TAG, "Зовнішня оперативна пам'ять PSRAM виявлена. Загальний обсяг: %u байт",
             (unsigned int)psram_size);

    wifi_init_softap();

    ov2640_config_t cam_config = {
        .pin_pwdn = CAM_PIN_PWDN,
        .pin_reset = CAM_PIN_RESET,
        .pin_xclk = CAM_PIN_XCLK,
        .pin_sscb_sda = CAM_PIN_SIOD,
        .pin_sscb_scl = CAM_PIN_SIOC,

        .pin_d7 = CAM_PIN_D7,
        .pin_d6 = CAM_PIN_D6,
        .pin_d5 = CAM_PIN_D5,
        .pin_d4 = CAM_PIN_D4,
        .pin_d3 = CAM_PIN_D3,
        .pin_d2 = CAM_PIN_D2,
        .pin_d1 = CAM_PIN_D1,
        .pin_d0 = CAM_PIN_D0,

        .pin_vsync = CAM_PIN_VSYNC,
        .pin_href = CAM_PIN_HREF,
        .pin_pclk = CAM_PIN_PCLK,

        .xclk_freq_hz = 20000000,
        .pix_format = PIXFORMAT_JPEG,
        .frame_size = FRAMESIZE_SVGA,
        .jpeg_quality = 12,
        .fb_count = 2
    };

    ESP_LOGI(TAG, "Ініціалізація драйвера камери OV2640...");
    ret = ov2640_init(&cam_config);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Ініціалізація камери завершилась помилкою 0x%x. Зупинка.", ret);
        return;
    }
    ESP_LOGI(TAG, "Камеру OV2640 успішно ініціалізовано.");

    httpd_handle_t server = mjpeg_server_start();
    if (!server) {
        ESP_LOGE(TAG, "Помилка запуску HTTP-сервера.");
        return;
    }

    xTaskCreate(system_monitor_task, "sys_monitor", 3072, NULL, 5, NULL);

    ESP_LOGI(TAG, "Систему повністю запущено. Підключіться до Wi-Fi '%s' та відкрийте http://192.168.4.1/stream",
             EXAMPLE_ESP_WIFI_SSID);
}
