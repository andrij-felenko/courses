#include <Arduino.h>

const int ssrPin = 4;

void setup() {
    pinMode(ssrPin, OUTPUT);
    digitalWrite(ssrPin, LOW);
}

void loop() {
    // Увімкнення навантаження 230 В
    digitalWrite(ssrPin, HIGH);
    delay(5000);

    // Вимкнення навантаження
    digitalWrite(ssrPin, LOW);
    delay(5000);
}
