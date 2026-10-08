// Приклад ініціалізації та керування виводом nSLEEP для DRV8833 у C++ (Arduino)
#include <Arduino.h>

const uint8_t PIN_DRV8833_NSLEEP = 4;
const uint8_t PIN_DRV8833_AIN1   = 5;
const uint8_t PIN_DRV8833_AIN2   = 6;

void setupDRV8833() {
    pinMode(PIN_DRV8833_NSLEEP, OUTPUT);
    pinMode(PIN_DRV8833_AIN1, OUTPUT);
    pinMode(PIN_DRV8833_AIN2, OUTPUT);

    // Початковий деактивований стан
    digitalWrite(PIN_DRV8833_NSLEEP, LOW);
    digitalWrite(PIN_DRV8833_AIN1, LOW);
    digitalWrite(PIN_DRV8833_AIN2, LOW);
}

void wakeUpDRV8833() {
    // Подача сигналу пробудження на nSLEEP
    digitalWrite(PIN_DRV8833_NSLEEP, HIGH);
    
    // Часова затримка для стабілізації внутрішньої помпи заряду VCP
    delay(2);
}
