#include <Arduino.h>
#include <WiFi.h>
#include "MjpegStreamServer.hpp"

// Налаштування точок доступу Wi-Fi мережі
const char* ssid     = "Your_WiFi_SSID";
const char* password = "Your_WiFi_Password";

// Об'єкт MJPEG відеосервера
static MjpegStreamServer streamServer;

void setup() {
    Serial.begin(115200);
    Serial.setDebugOutput(true);
    Serial.println();
    Serial.println("--- Запуск модуля ESP32-CAM (AI-Thinker) ---");

    // Підключення до Wi-Fi мережі
    WiFi.begin(ssid, password);
    Serial.print("Підключення до Wi-Fi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println();
    Serial.print("Wi-Fi підключено. IP-адреса пристрою: http://");
    Serial.println(WiFi.localIP());

    // Запуск MJPEG відеосервера
    if (streamServer.begin(80)) {
        Serial.print("MJPEG відеопотік доступний за адресою: http://");
        Serial.print(WiFi.localIP());
        Serial.println("/stream");
    } else {
        Serial.println("Помилка старту MJPEG відеосервера!");
    }
}

void loop() {
    // Вебсервер обробляється асинхронно в окремому завданні FreeRTOS
    vTaskDelay(pdMS_TO_TICKS(1000));
}
