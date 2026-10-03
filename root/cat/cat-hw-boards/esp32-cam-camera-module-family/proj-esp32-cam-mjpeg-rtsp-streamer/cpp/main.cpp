#include <Arduino.h>
#include <WiFi.h>
#include "CameraStreamer.hpp"

// Налаштування бездротової мережі Wi-Fi
const char* WIFI_SSID     = "Your_WiFi_SSID";
const char* WIFI_PASSWORD = "Your_WiFi_Password";

// Екземпляр головного класу-оркестратора відеострімера
CameraStreamer streamer;

void setup() {
    // Ініціалізація послідовного порту для виводу логів
    Serial.begin(115200);
    Serial.setDebugOutput(true);
    Serial.println();
    Serial.println(F("========================================="));
    Serial.println(F("  Запуск автономного відеострімера ESP32  "));
    Serial.println(F("========================================="));

    // Підключення до Wi-Fi мережі
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    Serial.printf("Підключення до Wi-Fi мережі '%s'...", WIFI_SSID);

    uint8_t retries = 0;
    while (WiFi.status() != WL_CONNECTED && retries < 30) {
        delay(500);
        Serial.print(".");
        retries++;
    }
    Serial.println();

    if (WiFi.status() != WL_CONNECTED) {
        Serial.println(F("[ПОМИЛКА] Не вдалося підключитися до Wi-Fi! Перевірте SSID та пароль."));
        return;
    }

    Serial.println(F("[ОК] Успішно підключено до Wi-Fi мережі."));
    Serial.print(F("IP-адреса пристрою: http://"));
    Serial.println(WiFi.localIP());
    Serial.print(F("Адреса MJPEG-стріму: http://"));
    Serial.print(WiFi.localIP());
    Serial.println(F("/stream"));

    // Запуск відеострімера (VGA роздільна здатність, quality=10, port=80)
    if (!streamer.begin(FRAMESIZE_VGA, 10, 80)) {
        Serial.println(F("[КРИТИЧНА ПОМИЛКА] Збій ініціалізації відеострімера!"));
        return;
    }

    Serial.println(F("Система повністю готова. Перейдіть за IP-адресою у браузері."));
}

void loop() {
    // Виклики фонової підтримки та телеметрії відеострімера
    streamer.update();

    // Невеликий відпочинок для збереження ресурсів процесора та відпрацювання задач FreeRTOS
    vTaskDelay(pdMS_TO_TICKS(100));
}
