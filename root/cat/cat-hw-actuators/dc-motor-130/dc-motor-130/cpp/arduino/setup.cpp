// Керування Н-мостом двигуна 130 на C++ (Arduino)
#include <Arduino.h>

const uint8_t PIN_IN1 = 9;   // ШІМ вивід напрямку A
const uint8_t PIN_IN2 = 10;  // ШІМ вивід напрямку B

void setup() {
    pinMode(PIN_IN1, OUTPUT);
    pinMode(PIN_IN2, OUTPUT);
    analogWrite(PIN_IN1, 0);
    analogWrite(PIN_IN2, 0);
}

void setMotorSpeed(int16_t speed) {
    // speed від -255 до 255
    if (speed > 0) {
        analogWrite(PIN_IN2, 0);
        analogWrite(PIN_IN1, constrain(speed, 0, 255));
    } else if (speed < 0) {
        analogWrite(PIN_IN1, 0);
        analogWrite(PIN_IN2, constrain(-speed, 0, 255));
    } else {
        analogWrite(PIN_IN1, 0);
        analogWrite(PIN_IN2, 0);
    }
}

void loop() {
    setMotorSpeed(200);  // Обертання вперед
    delay(2000);
    setMotorSpeed(0);    // Зупинка
    delay(500);
    setMotorSpeed(-200); // Обертання назад
    delay(2000);
    setMotorSpeed(0);
    delay(1000);
}
