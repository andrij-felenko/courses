#include <Arduino.h>
#include <WiFi.h>
#include <esp_log.h>
#include <esp_system.h>

#include "esp32_camera_wrapper.hpp"
#include "mjpeg_web_server.hpp"

static const char* TAG = "MainApp";

// Налаштування Wi-Fi з'єднання
static const char* WIFI_SSID = "ESP32_Camera_Net";
static const char* WIFI_PASS = "123456789";

// Глобальні екземпляри камери та веб-сервера
static Esp32CameraWrapper camera;
static MjpegWebServer webServer(camera, 80);

static uint32_t last_telemetry_time = 0;
static const uint32_t TELEMETRY_INTERVAL_MS = 5000;

void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println("\n=== ESP32-S3 Система Відеозахоплення та Асинхронний MJPEG Сервер ===");

    // 1. Конфігурація Wi-Fi мережі (спроба підключення до STA або запуск SoftAP)
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    Serial.printf("[Wi-Fi] Підключення до мережі %s ...\n", WIFI_SSID);

    uint8_t retries = 0;
    while (WiFi.status() != WL_CONNECTED && retries < 15) {
        delay(500);
        Serial.print(".");
        retries++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n[Wi-Fi] Успішно підключено!");
        Serial.printf("[Wi-Fi] IP адреса пристрою: %s\n", WiFi.localIP().toString().c_str());
    } else {
        Serial.println("\n[Wi-Fi] Не вдалося підключитися до STA. Запуск точки доступу SoftAP...");
        WiFi.mode(WIFI_AP);
        WiFi.softAP("ESP32-S3-CAM-AP", "123456789");
        Serial.printf("[Wi-Fi] IP адреса SoftAP: %s\n", WiFi.softAPIP().toString().c_str());
    }

    // 2. Налаштування та ініціалізація модуля камери ESP32-S3
    CameraConfig camConfig;
    camConfig.frame_size = FRAMESIZE_VGA;
    camConfig.jpeg_quality = 12;
    camConfig.fb_count = 2; // Подвійна буферизація у PSRAM

    if (!camera.init(camConfig)) {
        Serial.println("[ERROR] Критична помилка ініціалізації камери! Зупинка роботи.");
        while (true) {
            delay(1000);
        }
    }

    // 3. Запуск неблокуючого MJPEG / WebSocket веб-сервера
    if (!webServer.begin()) {
        Serial.println("[ERROR] Не вдалося запустити веб-сервер.");
    } else {
        Serial.println("[INFO] Асинхронний відеосервер успішно запущено.");
        Serial.println("[INFO] Відкрийте браузер за адресою пристрою для перегляду відеопотоку.");
    }
}

void loop() {
    // Періодичне обслуговування асинхронного розсилання кадрів через WebSocket
    webServer.update();

    // Періодичний моніторинг стану системи та вільної оперативної пам'яті PSRAM
    uint32_t now = millis();
    if (now - last_telemetry_time >= TELEMETRY_INTERVAL_MS) {
        last_telemetry_time = now;

        size_t free_heap = ESP.getFreeHeap();
        size_t free_psram = ESP.getFreePsram();
        uint32_t active_ws = webServer.getActiveWsClients();

        ESP_LOGI(TAG, "--- Системний стан ---");
        ESP_LOGI(TAG, "Вільна оперативна пам'ять Heap : %u байт (%u KB)", free_heap, free_heap / 1024);
        ESP_LOGI(TAG, "Вільна зовнішня пам'ять PSRAM  : %u байт (%u KB)", free_psram, free_psram / 1024);
        ESP_LOGI(TAG, "Активних WebSocket клієнтів    : %u", active_ws);
        ESP_LOGI(TAG, "----------------------");
    }
}
