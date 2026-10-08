#include <Arduino.h>

// Пін керування оптосимістором MOC3063
const uint8_t TRIAC_CTRL_PIN = 4;

void setup() {
    // Ініціалізація цифрового виходу керування
    pinMode(TRIAC_CTRL_PIN, OUTPUT);
    digitalWrite(TRIAC_CTRL_PIN, LOW);
}

void loop() {
    // Вмикання симістора: подача струму на LED оптопари
    digitalWrite(TRIAC_CTRL_PIN, HIGH);
    delay(5000);

    // Вимикання симістора: зняття струму з LED
    digitalWrite(TRIAC_CTRL_PIN, LOW);
    delay(5000);
}
