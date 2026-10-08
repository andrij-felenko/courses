#include <Arduino.h>

const uint8_t PIN_FORWARD_COIL  = 5;
const uint8_t PIN_REVERSE_COIL  = 6;
const uint8_t PIN_FORWARD_SENSE = 7;
const uint8_t PIN_REVERSE_SENSE = 8;

const unsigned long DEAD_TIME_MS = 150;

enum class MotorState {
    Stopped,
    Forward,
    Reverse
};

class ReversingStarterController {
private:
    MotorState currentState;

public:
    ReversingStarterController() : currentState(MotorState::Stopped) {}

    void begin() {
        pinMode(PIN_FORWARD_COIL, OUTPUT);
        pinMode(PIN_REVERSE_COIL, OUTPUT);
        digitalWrite(PIN_FORWARD_COIL, LOW);
        digitalWrite(PIN_REVERSE_COIL, LOW);

        pinMode(PIN_FORWARD_SENSE, INPUT_PULLUP);
        pinMode(PIN_REVERSE_SENSE, INPUT_PULLUP);
    }

    bool setDirection(MotorState targetState) {
        if (currentState == targetState) {
            return true;
        }

        // Знеструмлення обох котушок
        digitalWrite(PIN_FORWARD_COIL, LOW);
        digitalWrite(PIN_REVERSE_COIL, LOW);
        currentState = MotorState::Stopped;

        // Пауза деонізації дуги та механічної релаксації
        delay(DEAD_TIME_MS);

        // Контроль розмикання за допоміжними NC-контактами
        if (digitalRead(PIN_FORWARD_SENSE) == HIGH || digitalRead(PIN_REVERSE_SENSE) == HIGH) {
            return false; // Захисне блокування при приварюванні контактів
        }

        if (targetState == MotorState::Forward) {
            digitalWrite(PIN_FORWARD_COIL, HIGH);
            currentState = MotorState::Forward;
        } else if (targetState == MotorState::Reverse) {
            digitalWrite(PIN_REVERSE_COIL, HIGH);
            currentState = MotorState::Reverse;
        }

        return true;
    }
};
