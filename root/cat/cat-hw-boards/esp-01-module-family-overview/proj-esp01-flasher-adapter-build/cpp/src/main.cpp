#include <Arduino.h>
#include "EspModuleController.hpp"

// Створення екземпляра контролера для модуля ESP-01S.
// За потреби змініть параметр на ModuleRevision::Esp01 для класичного ESP-01.
EspModuleController espController(ModuleRevision::Esp01S);

// Змінні для неблокуючої затримки на основі millis()
unsigned long previousBlinkMillis = 0;
const unsigned long blinkIntervalMs = 500; // Період блимання 500 мс

unsigned long previousDiagMillis = 0;
const unsigned long diagIntervalMs = 5000; // Виведення діагностики кожні 5 секунд

void setup() {
    // Ініціалізація периферії модуля (UART та напрямок GPIO)
    espController.begin();

    // Первинне виведення інформації про модуль після старту
    espController.printDiagnosticInfo();
    Serial.println(F("Система успішно ініціалізована. Запуск основного циклу..."));
}

void loop() {
    unsigned long currentMillis = millis();

    // Неблокуюче керування світлодіодом (перемикання кожні 500 мс)
    if (currentMillis - previousBlinkMillis >= blinkIntervalMs) {
        previousBlinkMillis = currentMillis;
        
        espController.toggleLed();

        // Логування зміни стану в послідовний порт
        Serial.print(F("[LED] Стан змінено на: "));
        Serial.println(espController.isLedOn() ? F("УВІМКНЕНО") : F("ВИМКНЕНО"));
    }

    // Періодичний вивід розширеної діагностики кожні 5 секунд
    if (currentMillis - previousDiagMillis >= diagIntervalMs) {
        previousDiagMillis = currentMillis;

        Serial.println(F("[STATUS] Періодичний звіт працездатності прошивки:"));
        espController.printDiagnosticInfo();
    }
}
