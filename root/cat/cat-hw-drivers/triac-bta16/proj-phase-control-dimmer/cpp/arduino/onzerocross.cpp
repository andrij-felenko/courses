#include <Arduino.h>

const uint8_t ZC_PIN = 2;
const uint8_t TRIAC_PIN = 4;
volatile uint16_t delay_us = 5000;

// Переривання від детектора нуля відраховує затримку та генерує імпульс
void IRAM_ATTR onZeroCross() {
    delayMicroseconds(delay_us);
    digitalWrite(TRIAC_PIN, HIGH);
    delayMicroseconds(30);
    digitalWrite(TRIAC_PIN, LOW);
}

void setup() {
    pinMode(TRIAC_PIN, OUTPUT);
    pinMode(ZC_PIN, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(ZC_PIN), onZeroCross, FALLING);
}
