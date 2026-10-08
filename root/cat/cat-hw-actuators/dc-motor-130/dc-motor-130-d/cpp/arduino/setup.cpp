#include <Arduino.h>

const int MOTOR_IN1_PIN = 9;
const int MOTOR_IN2_PIN = 10;

void setup() {
    pinMode(MOTOR_IN1_PIN, OUTPUT);
    pinMode(MOTOR_IN2_PIN, OUTPUT);
    analogWrite(MOTOR_IN1_PIN, 0);
    analogWrite(MOTOR_IN2_PIN, 0);
}

// Встановлення швидкості й напрямку: speed від -255 до 255
void setMotorSpeed(int speed) {
    speed = constrain(speed, -255, 255);

    if (speed > 0) {
        // Обертання вперед
        analogWrite(MOTOR_IN1_PIN, speed);
        analogWrite(MOTOR_IN2_PIN, 0);
    } else if (speed < 0) {
        // Обертання назад
        analogWrite(MOTOR_IN1_PIN, 0);
        analogWrite(MOTOR_IN2_PIN, -speed);
    } else {
        // Динамічне гальмування через коротке замикання обмотки
        digitalWrite(MOTOR_IN1_PIN, HIGH);
        digitalWrite(MOTOR_IN2_PIN, HIGH);
    }
}

void loop() {
    // Приклад робочого циклу: розгін вперед, гальмування, реверс
    setMotorSpeed(200);
    delay(2000);

    setMotorSpeed(0); // Активне гальмування
    delay(1000);

    setMotorSpeed(-200);
    delay(2000);

    setMotorSpeed(0);
    delay(1000);
}
