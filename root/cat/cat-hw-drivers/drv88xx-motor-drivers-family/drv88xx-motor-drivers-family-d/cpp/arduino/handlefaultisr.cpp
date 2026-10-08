#include <Arduino.h>

const uint8_t PIN_NFAULT = 2;
const uint8_t PIN_ENABLE = 4;
volatile bool faultDetected = false;

void IRAM_ATTR handleFaultISR() {
    // Апаратне відключення силового каскаду
    digitalWrite(PIN_ENABLE, LOW);
    faultDetected = true;
}

void setup() {
    pinMode(PIN_NFAULT, INPUT_PULLUP);
    pinMode(PIN_ENABLE, OUTPUT);
    digitalWrite(PIN_ENABLE, HIGH);

    attachInterrupt(digitalPinToInterrupt(PIN_NFAULT), handleFaultISR, FALLING);
}

void loop() {
    if (faultDetected) {
        // Логування помилки та спроба повторного запуску після аналізу
        faultDetected = false;
        delay(1000); // Пауза безпеки перед повторним включенням
        digitalWrite(PIN_ENABLE, HIGH);
    }
}
