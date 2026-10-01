#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "esp_camera.h"
#include "esp_psram.h"

#include "camera_pins.h"
#include "mjpeg_server.h"

static const char *TAG = "main";

#define WIFI_SSID "ESP32-CAM-Stream"
#define WIFI_PASS "12345678"

// Ініціалізація апаратної частини та драйвера камери
static esp_err_t init_camera(void)
{
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = CAM_PIN_D0;
    config.pin_d1 = CAM_PIN_D1;
    config.pin_d2 = CAM_PIN_D2;
    config.pin_d3 = CAM_PIN_D3;
    config.pin_d4 = CAM_PIN_D4;
    config.pin_d5 = CAM_PIN_D5;
    config.pin_d6 = CAM_PIN_D6;
    config.pin_d7 = CAM_PIN_D7;
    config.pin_xclk = CAM_PIN_XCLK;
    config.pin_pclk = CAM_PIN_PCLK;
    config.pin_vsync = CAM_PIN_VSYNC;
    config.pin_href = CAM_PIN_HREF;
    config.pin_siod = CAM_PIN_SIOD;
    config.pin_sioc = CAM_PIN_SIOC;
    config.pin_pwdn = CAM_PIN_PWDN;
    config.pin_reset = CAM_PIN_RESET;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;

    // Перевірка наявності зовнішньої пам'яті PSRAM для вибору роздільності
    if (esp_psram_is_initialized()) {
        ESP_LOGI(TAG, "Виявлено зовнішню PSRAM: підключення UXGA кадрових буферів");
        config.frame_size = FRAMESIZE_UXGA;
        config.jpeg_quality = 10;
        config.fb_count = 2;
        config.grab_mode = CAMERA_GRAB_LATEST;
        config.fb_location = CAMERA_FB_IN_PSRAM;
    } else {
        ESP_LOGW(TAG, "PSRAM не виявлено! Обмеження роздільності до SVGA та розміщення в SRAM");
        config.frame_size = FRAMESIZE_SVGA;
        config.jpeg_quality = 12;
        config.fb_count = 1;
        config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
        config.fb_location = CAMERA_FB_IN_DRAM;
    }

    // Ініціалізація драйвера камери
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації драйвера камери: 0x%x", err);
        return err;
    }

    sensor_t *s = esp_camera_sensor_get();
    if (s != NULL) {
        // Оптимізація якості зображення для сенсора OV2640
        s->set_vflip(s, 1);       // Вертикальне відображення
        s->set_hmirror(s, 1);     // Дзеркальне відображення по горизонталі
    }

    ESP_LOGI(TAG, "Успішна ініціалізація камери");
    return ESP_OK;
}

// Конфігурація Wi-Fi у режимі точці доступу (SoftAP)
static void init_wifi(void)
{
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_ap();

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));

    wifi_config_t wifi_config = {
        .ap = {
            .ssid = WIFI_SSID,
            .ssid_len = strlen(WIFI_SSID),
            .channel = 1,
            .password = WIFI_PASS,
            .max_connection = 4,
            .authmode = WIFI_AUTH_WPA2_PSK,
        },
    };

    if (strlen(WIFI_PASS) == 0) {
        wifi_config.ap.authmode = WIFI_AUTH_OPEN;
    }

    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_AP));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_AP, &wifi_config));
    ESP_ERROR_CHECK(esp_wifi_start());

    ESP_LOGI(TAG, "Точку доступу Wi-Fi створено. SSID:%s пароль:%s", WIFI_SSID, WIFI_PASS);
}

void app_main(void)
{
    // Ініціалізація NVS для роботи мережевого стека
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    // Ініціалізація сенсора камери
    if (init_camera() != ESP_OK) {
        ESP_LOGE(TAG, "Зупинка запуску через помилку камери");
        return;
    }

    // Запуск Wi-Fi та сервера потокового відео
    init_wifi();
    start_mjpeg_server();

    ESP_LOGI(TAG, "Вузол відеоспостереження ESP32-CAM успішно запущено");
}
