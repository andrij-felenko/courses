#include <Arduino.h>
#include "Esp01Adapter.hpp"

// Призначення виводів SoftwareSerial для підключення адаптера ESP-01
// Pin 2 Arduino (RX) підключається до TX модуля ESP-01
// Pin 3 Arduino (TX) підключається до RX модуля ESP-01 (через адаптер живлення/рівнів)
constexpr uint8_t ESP_RX_PIN = 2;
constexpr uint8_t ESP_TX_PIN = 3;

// Екземпляр адаптера ESP-01
Esp01Adapter espAdapter(ESP_RX_PIN, ESP_TX_PIN);

void setup() {
    // Ініціалізація апаратного порту Serial для зв'язку з комп'ютером (Serial Monitor)
    Serial.begin(9600);
    while (!Serial) {
        ; // Чекаємо на відкриття порту (актуально для плат Arduino Leonardo/Micro)
    }

    Serial.println(F("=================================================="));
    Serial.println(F("  Запуск мосту Arduino <-> ESP-01 (SoftwareSerial) "));
    Serial.println(F("=================================================="));

    // Ініціалізація програмного порту SoftwareSerial на швидкості 9600 бод
    espAdapter.begin(9600);

    // Початкова діагностика зв'язку з модулем
    Serial.println(F("[INFO] Перевірка реагування ESP-01 на команду AT..."));
    String testResp = espAdapter.sendCommand("AT", 1000);
    if (testResp.indexOf("OK") != -1) {
        Serial.println(F("[OK] Модуль ESP-01 активний і відповідає!"));
    } else {
        Serial.println(F("[WARN] Модуль не повернув 'OK'. Перевірте швидкість та живлення 3.3V."));
    }

    // Автоматичне сканування Wi-Fi мереж при старті програми
    espAdapter.scanNetworks();

    Serial.println(F("\n[READY] Режим прозорого мосту активовано."));
    Serial.println(F("Вводьте AT-команди у Serial Monitor для відправки на модуль:"));
}

void loop() {
    // Безперервна двостороння ретрансляція даних у реальному часі
    espAdapter.processBridge();
}
