#include <Arduino.h>

const int PIN_PL = 8;
const int PIN_CP = 9;
const int PIN_Q7 = 10;

void setup() {
    pinMode(PIN_PL, OUTPUT);
    pinMode(PIN_CP, OUTPUT);
    pinMode(PIN_Q7, INPUT);
    
    digitalWrite(PIN_PL, HIGH);
    digitalWrite(PIN_CP, LOW);
}

uint8_t readHC165() {
    uint8_t data = 0;
    
    digitalWrite(PIN_PL, LOW);
    delayMicroseconds(1);
    digitalWrite(PIN_PL, HIGH);
    delayMicroseconds(1);
    
    for (int i = 0; i < 8; i++) {
        int bit = digitalRead(PIN_Q7);
        data |= (bit << (7 - i));
        
        digitalWrite(PIN_CP, HIGH);
        delayMicroseconds(1);
        digitalWrite(PIN_CP, LOW);
        delayMicroseconds(1);
    }
    
    return data;
}
