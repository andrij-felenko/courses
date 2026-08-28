// ESP32: ECHO — ТІЛЬКИ через подільник 1к/2к (5 В → ~3.3 В).
// TRIG — напряму. VCC модуля — 5 В (не 3.3!).
#include <NewPing.h>

const uint8_t TRIG_PIN = 5;
const uint8_t ECHO_PIN = 18;   // сюди приходить середина подільника
const unsigned int MAX_DISTANCE = 300;

NewPing sonar(TRIG_PIN, ECHO_PIN, MAX_DISTANCE);

void setup() {
    Serial.begin(115200);
}

void loop() {
    delay(60);
    unsigned int cm = sonar.convert_cm(sonar.ping_median(5));
    if (cm == 0) Serial.println("out of range");
    else       { Serial.printf("%u cm\n", cm); }
}
