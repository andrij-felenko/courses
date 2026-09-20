#include <Arduino.h>

const int pinPL = 4;
const int pinCP = 5;
const int pinQ7 = 18;

uint16_t readDIPSwitchesCascade() {
    uint16_t data = 0;
    
    digitalWrite(pinPL, LOW);
    delayMicroseconds(1);
    digitalWrite(pinPL, HIGH);
    
    for (int i = 0; i < 16; i++) {
        data <<= 1;
        if (digitalRead(pinQ7) == HIGH) {
            data |= 0x0001;
        }
        digitalWrite(pinCP, HIGH);
        delayMicroseconds(1);
        digitalWrite(pinCP, LOW);
        delayMicroseconds(1);
    }
    return data;
}
