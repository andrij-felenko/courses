#include <Arduino.h>

const uint8_t PIN_KM1_FORWARD = 8;
const uint8_t PIN_KM2_REVERSE = 9;
const uint32_t DEAD_TIME_MS   = 500;

enum MotorState {
    MOTOR_STOP = 0,
    MOTOR_FORWARD,
    MOTOR_REVERSE
};

MotorState currentState = MOTOR_STOP;

void setupMotor() {
    pinMode(PIN_KM1_FORWARD, OUTPUT);
    pinMode(PIN_KM2_REVERSE, OUTPUT);
    digitalWrite(PIN_KM1_FORWARD, LOW);
    digitalWrite(PIN_KM2_REVERSE, LOW);
}

bool setMotorState(MotorState newState) {
    if (currentState == newState) {
        return true;
    }

    // Знімаємо напругу з обох котушок контакторів
    digitalWrite(PIN_KM1_FORWARD, LOW);
    digitalWrite(PIN_KM2_REVERSE, LOW);

    // Пауза затримки для гасіння комутаційної дуги
    delay(DEAD_TIME_MS);

    if (newState == MOTOR_FORWARD) {
        digitalWrite(PIN_KM1_FORWARD, HIGH);
    } else if (newState == MOTOR_REVERSE) {
        digitalWrite(PIN_KM2_REVERSE, HIGH);
    }

    currentState = newState;
    return true;
}
