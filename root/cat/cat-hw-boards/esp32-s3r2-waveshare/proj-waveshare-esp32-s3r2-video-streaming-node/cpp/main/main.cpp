#include <esp_log.h>
#include <esp_system.h>
#include <esp_wifi.h>
#include <nvs_flash.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

#include "camera_driver.hpp"
#include "http_stream_server.hpp"
#include "usb_uvc_device.hpp"

static const char* TAG = "MainApp";

static void init_wifi_ap() {
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_ap();

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));

    wifi_config_t wifi_config = {};
    uint8_t ssid[] = "ESP32S3-CamServer";
    uint8_t pass[] = "12345678";
    memcpy(wifi_config.ap.ssid, ssid, sizeof(ssid));
    memcpy(wifi_config.ap.password, pass, sizeof(pass));
    wifi_config.ap.ssid_len = strlen((char*)ssid);
    wifi_config.ap.channel = 1;
    wifi_config.ap.authmode = WIFI_AUTH_WPA2_PSK;
    wifi_config.ap.max_connection = 4;

    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_AP));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_AP, &wifi_config));
    ESP_ERROR_CHECK(esp_wifi_start());

    ESP_LOGI(TAG, "Wi-Fi точку доступу створено. SSID: %s, IP: 192.168.4.1", ssid);
}

extern "C" void app_main() {
    ESP_LOGI(TAG, "Запуск прошивки автономного відеосервера Waveshare ESP32-S3R2");

    // Ініціалізація енергонезалежної пам'яті NVS
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    // Ініціалізація мережі Wi-Fi у режимі точки доступу
    init_wifi_ap();

    // Створюємо та ініціалізуємо драйвер камери
    auto camera = std::make_unique<esp32s3::CameraDriver>();
    if (!camera->init()) {
        ESP_LOGE(TAG, "Критична помилка ініціалізації камери. Запуск зупинено");
        return;
    }

    // Запускаємо HTTP MJPEG-відеосервер для Wi-Fi трансляції
    auto http_server = std::make_unique<esp32s3::HttpStreamServer>(*camera);
    if (!http_server->start(80)) {
        ESP_LOGE(TAG, "Не вдалося запустити HTTP-відеосервер");
    }

    // Ініціалізуємо модуль USB UVC для нативного перемикання в режим веб-камери
    auto usb_uvc = std::make_unique<esp32s3::UsbUvcDevice>(*camera);
    if (usb_uvc->init()) {
        usb_uvc->start_streaming_task();
    }

    ESP_LOGI(TAG, "Всі підсистеми успішно запущено. Моніторинг стану пристрою...");

    // Головний цикл фонового моніторингу та діагностики купи пам'яті
    while (true) {
        vTaskDelay(pdMS_TO_TICKS(10000));
        size_t free_sram = heap_caps_get_free_size(MALLOC_CAP_INTERNAL);
        size_t free_psram = heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
        bool usb_active = usb_uvc->is_connected();

        ESP_LOGI(TAG, "Стан системи: Вільна SRAM: %u байтів, Вільна PSRAM: %u байтів | USB UVC: %s",
                 free_sram, free_psram, usb_active ? "АКТИВНИЙ" : "очікування");
    }
}
