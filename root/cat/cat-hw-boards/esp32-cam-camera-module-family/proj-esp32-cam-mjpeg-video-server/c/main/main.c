#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "nvs_flash.h"

#include "app_camera.h"

// Зовнішнє оголошення функції старту HTTP-сервера з app_httpd.c
esp_err_t app_httpd_start(void);

static const char *TAG = "main";

#define EXAMPLE_ESP_WIFI_SSID      "ESP32_CAM_AP"
#define EXAMPLE_ESP_WIFI_PASS      "12345678"

/**
 * @brief Проста ініціалізація Wi-Fi у режимі SoftAP для автономного підключення клієнтів.
 */
static void wifi_init_softap(void)
{
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_ap();

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));

    wifi_config_t wifi_config = {
        .ap = {
            .ssid = EXAMPLE_ESP_WIFI_SSID,
            .ssid_len = strlen(EXAMPLE_ESP_WIFI_SSID),
            .channel = 1,
            .password = EXAMPLE_ESP_WIFI_PASS,
            .max_connection = 4,
            .authmode = WIFI_AUTH_WPA_WPA2_PSK
        },
    };

    if (strlen(EXAMPLE_ESP_WIFI_PASS) == 0) {
        wifi_config.ap.authmode = WIFI_AUTH_OPEN;
    }

    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_AP));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_AP, &wifi_config));
    ESP_ERROR_CHECK(esp_wifi_start());

    ESP_LOGI(TAG, "Точку доступу Wi-Fi SoftAP запущено. SSID: %s", EXAMPLE_ESP_WIFI_SSID);
}

void app_main(void)
{
    // Ініціалізація енергонезалежної пам'яті NVS
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    ESP_LOGI(TAG, "Ініціалізація системних компонентів ESP32-CAM...");

    // 1. Налаштування мережі Wi-Fi
    wifi_init_softap();

    // 2. Ініціалізація сенсора камери OV2640
    if (app_camera_init() != ESP_OK) {
        ESP_LOGE(TAG, "Критична помилка ініціалізації камери. Роботу зупинено.");
        return;
    }

    // 3. Запуск HTTP-відеосервера потокового мовлення
    if (app_httpd_start() != ESP_OK) {
        ESP_LOGE(TAG, "Критична помилка старту HTTP-сервера.");
        return;
    }

    ESP_LOGI(TAG, "Відеосервер готовий: перейдіть за адресою http://192.168.4.1/stream");
}
