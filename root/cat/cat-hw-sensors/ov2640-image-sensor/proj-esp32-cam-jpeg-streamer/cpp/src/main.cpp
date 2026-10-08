#include <Arduino.h>
#include <WiFi.h>
#include "camera_config.hpp"
#include "esp_camera_wrapper.hpp"
#include "mjpeg_stream_server.hpp"

// Налаштування точки доступу Wi-Fi (SoftAP)
const char* WIFI_SSID = "ESP32-CAM-Stream";
const char* WIFI_PASS = "12345678";

// Екземпляри камери та вебсервера
EspCamera g_camera(CameraPinConfig::getAiThinkerConfig());
MjpegStreamServer g_stream_server(g_camera, 80);

void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println();
    Serial.println(F("=================================================="));
    Serial.println(F("  Система відеотрансляції OV2640 на ESP32 (C++)   "));
    Serial.println(F("=================================================="));

    // Ініціалізація Wi-Fi у режимі точки доступу (SoftAP)
    WiFi.mode(WIFI_AP);
    if (WiFi.softAP(WIFI_SSID, WIFI_PASS)) {
        Serial.printf("[Main] Wi-Fi Точку доступу створено. SSID: %s\n", WIFI_SSID);
        Serial.print(F("[Main] IP-адреса сервера: http://"));
        Serial.println(WiFi.softAPIP());
    } else {
        Serial.println(F("[Main] Помилка створення Wi-Fi точки доступу!"));
    }

    // Ініціалізація камери OV2640
    if (!g_camera.init(FRAMESIZE_VGA, PIXFORMAT_JPEG)) {
        Serial.println(F("[Main] КРИТИЧНА ПОМИЛКА: Не вдалося ініціалізувати камеру OV2640!"));
        return;
    }

    // Додаткові налаштування зорових параметрів камери
    g_camera.setVFlip(true);
    g_camera.setQuality(10);

    // Запуск HTTP-сервера трансляції
    g_stream_server.begin();

    Serial.println(F("=================================================="));
    Serial.println(F("  Трансляція готова! Для перегляду відкрийте:   "));
    Serial.print(F("  http://"));
    Serial.print(WiFi.softAPIP());
    Serial.println(F("/stream або http://192.168.4.1/"));
    Serial.println(F("=================================================="));
}

void loop() {
    // Обслуговування вхідних HTTP-запитів
    g_stream_server.handleClient();

    // Періодична діагностика використання пам'яті (кожні 10 секунд)
    static uint32_t last_diag_time = 0;
    if (millis() - last_diag_time >= 10000) {
        last_diag_time = millis();
        Serial.printf("[System] Вільна internal SRAM: %u байт, Вільна PSRAM: %u байт\n",
                      ESP.getFreeHeap(), ESP.getFreePsram());
    }
}
