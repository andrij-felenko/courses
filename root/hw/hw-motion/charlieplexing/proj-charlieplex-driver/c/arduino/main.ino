#include <Arduino.h>

static const uint8_t PINS[4] = {2, 3, 4, 5};

void halSetHigh(uint8_t pin) {
    uint8_t p = PINS[pin];
    pinMode(p, OUTPUT);
    digitalWrite(p, HIGH);
}

void halSetLow(uint8_t pin) {
    uint8_t p = PINS[pin];
    pinMode(p, OUTPUT);
    digitalWrite(p, LOW);
}

void halSetHiZ(uint8_t pin) {
    uint8_t p = PINS[pin];
    pinMode(p, INPUT);
    digitalWrite(p, LOW); // Примусово вимикаємо внутрішній Pull-Up резистор
}
