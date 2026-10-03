#include <Arduino.h>

enum DriverState {
    STATE_IDLE,
    STATE_CONNECTING,
    STATE_WAIT_PROMPT,
    STATE_WAIT_SEND_OK,
    STATE_CLOSING,
    STATE_RECOVERY
};

class AsyncSocketDriver {
private:
    DriverState m_state;
    uint32_t m_lastStateChangeMs;
    const uint32_t FSM_TIMEOUT_MS = 3250;

public:
    AsyncSocketDriver() : m_state(STATE_IDLE), m_lastStateChangeMs(0) {}

    // Неблокуюча обробка автомата у головному циклі loop()
    void loop() {
        uint32_t now = millis();

        switch (m_state) {
        case STATE_IDLE:
            // Чекаємо зовнішньої команди
            break;

        case STATE_CONNECTING:
            if (Serial.find("CONNECT")) {
                Serial.println("AT+CIPSEND=0,32");
                setState(STATE_WAIT_PROMPT, now);
            } else if (now - m_lastStateChangeMs > FSM_TIMEOUT_MS) {
                setState(STATE_RECOVERY, now);
            }
            break;

        case STATE_WAIT_PROMPT:
            if (Serial.find(">")) {
                Serial.print("DataPayloadBytes...");
                setState(STATE_WAIT_SEND_OK, now);
            } else if (now - m_lastStateChangeMs > 2000) {
                setState(STATE_RECOVERY, now);
            }
            break;

        case STATE_WAIT_SEND_OK:
            if (Serial.find("SEND OK")) {
                Serial.println("AT+CIPCLOSE=0");
                setState(STATE_CLOSING, now);
            } else if (now - m_lastStateChangeMs > 3000) {
                setState(STATE_RECOVERY, now);
            }
            break;

        case STATE_CLOSING:
            if (Serial.find("OK") || Serial.find("CLOSED")) {
                setState(STATE_IDLE, now);
            } else if (now - m_lastStateChangeMs > 1000) {
                setState(STATE_IDLE, now);
            }
            break;

        case STATE_RECOVERY:
            Serial.println("AT+CIPCLOSE=0");
            setState(STATE_IDLE, now);
            break;
        }
    }

    void startConnection() {
        if (m_state == STATE_IDLE) {
            Serial.println("AT+CIPSTART=0,\"TCP\",\"192.168.1.100\",8080");
            setState(STATE_CONNECTING, millis());
        }
    }

private:
    void setState(DriverState newState, uint32_t now) {
        m_state = newState;
        m_lastStateChangeMs = now;
    }
};
