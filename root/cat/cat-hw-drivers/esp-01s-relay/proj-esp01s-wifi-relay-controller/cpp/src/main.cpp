#include <Arduino.h>
#include "RelayController.h"
#include "NetworkManager.h"

// Параметри підключення до Wi-Fi
const char* WIFI_SSID = "Your_WiFi_SSID";
const char* WIFI_PASS = "Your_WiFi_Password";

// Параметри MQTT-брокера
const char* MQTT_SERVER = "192.168.1.100";
const uint16_t MQTT_PORT = 1883;
const char* MQTT_USER   = "";
const char* MQTT_PASS   = "";

// Об'єкт керування реле (GPIO0, Active LOW за замовчуванням для ESP-01S)
RelayController relay(0, true);

// Мережевий менеджер для HTTP та MQTT
NetworkManager netManager(relay);

void setup() {
    // Ініціалізація послідовного порту для виводу налагоджувальної інформації
    Serial.begin(115200);
    delay(100);
    Serial.println();
    Serial.println(F("=========================================="));
    Serial.println(F("  ESP-01S Relay Module Control Firmware   "));
    Serial.println(F("=========================================="));

    // Ініціалізація контролера реле та відновлення стану з EEPROM
    relay.begin();

    // Запуск мережевого менеджера (Wi-Fi, HTTP вебсервер, MQTT)
    netManager.begin(WIFI_SSID, WIFI_PASS, MQTT_SERVER, MQTT_PORT, MQTT_USER, MQTT_PASS);

    Serial.println(F("Систему успішно ініціалізовано. Пристрій готовий."));
}

void loop() {
    // Основний цикл обробки мережевих подій
    netManager.loop();
}
