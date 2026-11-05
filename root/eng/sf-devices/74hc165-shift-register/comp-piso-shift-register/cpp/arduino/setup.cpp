#include <Arduino.h>

const int pl_pin = 8;
const int clk_pin = 9;
const int q_pin = 10;

void setup() {
    pinMode(pl_pin, OUTPUT);
    pinMode(clk_pin, OUTPUT);
    pinMode(q_pin, INPUT);
    
    digitalWrite(pl_pin, HIGH);
    digitalWrite(clk_pin, LOW);
}

uint8_t piso_read_byte() {
    digitalWrite(pl_pin, LOW);
    delayMicroseconds(1);
    digitalWrite(pl_pin, HIGH);
    delayMicroseconds(1);
    
    return shiftIn(q_pin, clk_pin, MSBFIRST);
}
