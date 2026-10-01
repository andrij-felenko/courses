#include <cstdio>
#include <cstring>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "nvs_flash.h"
#include "ov3640_camera.hpp"
#include "web_server.hpp"

static const char* TAG = "main_cpp";

#define WIFI_SSID "ESP32_CAM_OV3640_CPP"
#define WIFI_PASS "12345678"

static void init_wifi_ap() {
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_ap();

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));

    wifi_config_t wifi_config = {};
    std::strcpy(reinterpret_cast<char*>(wifi_config.ap.ssid), WIFI_SSID);
    wifi_config.ap.ssid_len = std::strlen(WIFI_SSID);
    std::strcpy(reinterpret_cast<char*>(wifi_config.ap.password), WIFI_PASS);
    wifi_config.ap.max_connection = 4;
    wifi_config.ap.authmode = WIFI_AUTH_WPA2_PSK;

    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_AP));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_AP, &wifi_config));
    ESP_ERROR_CHECK(esp_wifi_start());

    ESP_LOGI(TAG, "Wi-Fi Точка доступу створена. SSID: %s, IP: 192.168.4.1", WIFI_SSID);
}

extern "C" void app_main(void) {
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    ESP_LOGI(TAG, "Запуск C++ прошивки ESP32-CAM (OV3640)...");

    static Ov3640Camera camera;
    if (camera.init() != ESP_OK) {
        ESP_LOGE(TAG, "Критична помилка ініціалізації камери. Зупинка.");
        return;
    }

    init_wifi_ap();

    static CameraWebServer web_server(camera);
    if (web_server.start(80) != ESP_OK) {
        ESP_LOGE(TAG, "Критична помилка запуску веб-сервера.");
        return;
    }

    ESP_LOGI(TAG, "Систему C++ готово до роботи.");
}
