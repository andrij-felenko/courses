// Arduino Uno: спати глибоко, будитися сторожовим таймером, міряти рідко.
#include <LowPower.h>

const uint8_t POWER = 7;
const uint8_t SOIL  = A0;

int median9() { /* як вище */ return analogRead(SOIL); }

void measureAndDecide() {
    digitalWrite(POWER, HIGH);
    delay(10);
    int v = median9();
    digitalWrite(POWER, LOW);
    // тут рішення: полив / тривога
    Serial.print("вологість="); Serial.println(v);
    Serial.flush();
}

void setup() {
    pinMode(POWER, OUTPUT);
    digitalWrite(POWER, LOW);
    Serial.begin(9600);
}

void loop() {
    measureAndDecide();
    // спимо ~30 хв = 225 · 8 с у режимі найглибшого сну
    for (int i = 0; i < 225; i++)
        LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
}
