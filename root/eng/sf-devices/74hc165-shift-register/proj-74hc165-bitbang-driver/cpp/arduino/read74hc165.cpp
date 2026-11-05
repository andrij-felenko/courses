#include <Arduino.h>

uint8_t read74HC165(uint8_t pinPL, uint8_t pinCP, uint8_t pinQ7) {
    uint8_t data = 0;

    // Фіксація паралельних даних у внутрішній регістр
    digitalWrite(pinPL, LOW);
    delayMicroseconds(1);
    digitalWrite(pinPL, HIGH);
    delayMicroseconds(1);

    // Зчитування 8 біт (зсув вліво)
    for (int i = 0; i < 8; i++) {
        uint8_t bitVal = digitalRead(pinQ7);
        data = (data << 1) | bitVal;

        // Тактовий імпульс
        digitalWrite(pinCP, HIGH);
        delayMicroseconds(1);
        digitalWrite(pinCP, LOW);
        delayMicroseconds(1);
    }

    return data;
}
