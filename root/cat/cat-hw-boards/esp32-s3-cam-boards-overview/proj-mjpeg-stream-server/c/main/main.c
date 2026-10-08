#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "nvs_flash.h"

#include "camera_driver.h"
#include "mjpeg_stream_server.h"
#include "power_adc.h"

static const char *TAG = "MAIN_APP";

#define WIFI_AP_SSID      "ESP32S3-CAM-STREAM"
#define WIFI_AP_PASS      "12345678"
#define WIFI_AP_MAX_CONN  4

static void wifi_init_softap(void)
{
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_ap();

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));

    wifi_config_t wifi_config = {
        .ap = {
            .ssid = WIFI_AP_SSID,
            .ssid_len = strlen(WIFI_AP_SSID),
            .channel = 1,
            .password = WIFI_AP_PASS,
            .max_connection = WIFI_AP_MAX_CONN,
            .authmode = WIFI_AUTH_WPA2_PSK,
        },
    };

    if (strlen(WIFI_AP_PASS) == 0) {
        wifi_config.ap.authmode = WIFI_AUTH_OPEN;
    }

    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_AP));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_AP, &wifi_config));
    ESP_ERROR_CHECK(esp_wifi_start());

    ESP_LOGI(TAG, "Wi-Fi Точку доступу (SoftAP) запущено. SSID: %s, IP: 192.168.4.1", WIFI_AP_SSID);
}

static void power_monitor_task(void *pvParameters)
{
    power_adc_config_t adc_cfg;
    esp_err_t err = power_adc_init(&adc_cfg);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося ініціалізувати АЦП для задачі моніторингу");
        vTaskDelete(NULL);
        return;
    }

    ESP_LOGI(TAG, "Задачу FreeRTOS для моніторингу АЦП запущено на ядрі %d", xPortGetCoreID());

    while (1) {
        uint32_t voltage_mv = 0;
        err = power_adc_read_voltage(&adc_cfg, &voltage_mv);
        if (err == ESP_OK) {
            float voltage_v = (float)voltage_mv / 1000.0f;
            ESP_LOGI(TAG, "[Монітор живлення] Напруга = %.2f В (%u мВ)", voltage_v, (unsigned int)voltage_mv);
        } else {
            ESP_LOGE(TAG, "[Монітор живлення] Помилка зчитування напруги АЦП");
        }

        vTaskDelay(pdMS_TO_TICKS(3000));
    }

    power_adc_deinit(&adc_cfg);
    vTaskDelete(NULL);
}

void app_main(void)
{
    ESP_LOGI(TAG, "Старт системи відеозахоплення ESP32-S3...");

    /* 1. Ініціалізація NVS (Non-Volatile Storage) */
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    /* 2. Ініціалізація мережі Wi-Fi в режимі Точки доступу (SoftAP) */
    wifi_init_softap();

    /* 3. Конфігурація та ініціалізація DVP-камери з буферизацією в PSRAM */
    ret = camera_driver_init();
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Критична помилка: Не вдалося ініціалізувати камеру!");
        return;
    }

    /* 4. Розгортання HTTP MJPEG відеосервера */
    httpd_handle_t server = NULL;
    ret = mjpeg_stream_server_start(&server);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Критична помилка: Не вдалося запустити MJPEG HTTP-сервер!");
        return;
    }

    /* 5. Запуск окремої задачі FreeRTOS для вимірювання АЦП без затримок у відеопотоці */
    xTaskCreatePinnedToCore(
        power_monitor_task,
        "power_adc_task",
        4096,
        NULL,
        5,
        NULL,
        0
    );

    ESP_LOGI(TAG, "Систему ESP32-S3 CAM успішно розгорнуто!");
    ESP_LOGI(TAG, "Переглядайте MJPEG відеопотік за адресою: http://192.168.4.1/stream");
}
