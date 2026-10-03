// Приклад реалізації FSM-парсера ESP-AT відповідей на C++ (Arduino)
#include <Arduino.h>

enum class ATState {
    Idle,
    WaitResponse,
    Success,
    Error,
    Timeout
};

class ATHostParser {
private:
    String lineBuffer;
    ATState currentState;
    unsigned long startTime;
    unsigned long timeoutMs;

public:
    ATHostParser() : currentState(ATState::Idle), startTime(0), timeoutMs(1000) {}

    void sendCommand(Stream &serial, const String &cmd, unsigned long timeout) {
        lineBuffer = "";
        timeoutMs = timeout;
        startTime = millis();
        currentState = ATState::WaitResponse;
        serial.print(cmd + "\r\n");
    }

    ATState update(Stream &serial) {
        if (currentState != ATState::WaitResponse) {
            return currentState;
        }

        while (serial.available() > 0) {
            char c = serial.read();
            if (c == '\r') continue;
            if (c == '\n') {
                if (lineBuffer.length() > 0) {
                    ATState result = parseLine(lineBuffer);
                    lineBuffer = "";
                    if (result != ATState::WaitResponse) {
                        currentState = result;
                        return currentState;
                    }
                }
            } else {
                lineBuffer += c;
            }
        }

        if (millis() - startTime >= timeoutMs) {
            currentState = ATState::Timeout;
        }
        return currentState;
    }

private:
    ATState parseLine(const String &line) {
        if (line == "OK") {
            return ATState::Success;
        } else if (line == "ERROR" || line.startsWith("+CME ERROR")) {
            return ATState::Error;
        } else if (line.startsWith("+") || line.startsWith("WIFI ")) {
            // Обробка асинхронних URC сповіщень
            Serial.println("URC: " + line);
        }
        return ATState::WaitResponse;
    }
};
