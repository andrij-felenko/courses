#include <Arduino.h>
#include "Esp01Tester.hpp"

// Налаштування користувацької конфігурації для модуля ESP-01
// За замовчуванням світлодіод підключено до GPIO1 (TX0) або GPIO2 (в залежності від модифікації ESP-01/ESP-01S)
static const UartConfig uartSettings{115200};
static const GpioConfig gpioSettings{1, true}; // GPIO1, activeLow = true

// Створення глобального об'єкта тестера модуля ESP-01
Esp01Tester tester(uartSettings, gpioSettings);

// Часові інтервали для неблокуючого виконання циклу в loop()
static uint32_t lastToggleTime = 0;
static const uint32_t TOGGLE_INTERVAL_MS = 1000; // Інтервал перемикання LED (1 сек)

static uint32_t lastInfoTime = 0;
static const uint32_t INFO_INTERVAL_MS = 10000;  // Інтервал повторного виведення діагностики (10 сек)

static uint32_t cycleCounter = 0;

void setup() {
    // Ініціалізація послідовного порту та настройка GPIO
    tester.begin();

    // Первинне виведення детальної системної інформації при старті
    tester.printSystemInfo();

    Serial.println(F("[ІНФО] Розпочато періодичний цикл тестування..."));
    Serial.println(F("[ІНФО] Якщо LED миготить і повідомлення надходять у Serial Monitor —"));
    Serial.println(F("       адаптер-програматор та ESP-01 працюють коректно."));
}

void loop() {
    uint32_t currentMillis = millis();

    // Неблокуюче миготіння світлодіодом через фіксований інтервал часу
    if (currentMillis - lastToggleTime >= TOGGLE_INTERVAL_MS) {
        lastToggleTime = currentMillis;
        cycleCounter++;

        // Перемикання стану світлодіода
        tester.toggleLed();

        // Надсилання статусного повідомлення в Serial Monitor
        tester.printHeartbeat(cycleCounter);
    }

    // Періодичний вивід розширеної системної інформації
    if (currentMillis - lastInfoTime >= INFO_INTERVAL_MS) {
        lastInfoTime = currentMillis;
        tester.printSystemInfo();
    }
}
