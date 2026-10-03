#include <Arduino.h>

class CipsendFSM {
public:
    enum class State { Idle, SendCmd, WaitPrompt, PumpPayload, WaitResult, ErrorRecovery };

private:
    State state = State::Idle;
    uint8_t linkId = 0;
    const uint8_t* payload = nullptr;
    uint16_t payloadLen = 0;
    uint32_t timerStart = 0;
    uint8_t prevRxByte = 0;

public:
    bool startSend(uint8_t id, const uint8_t* data, uint16_t len) {
        if (state != State::Idle || !data || len == 0) return false;
        linkId = id;
        payload = data;
        payloadLen = len;
        timerStart = millis();
        state = State::SendCmd;
        return true;
    }

    void tick(HardwareSerial& serial) {
        uint32_t currentMs = millis();

        switch (state) {
            case State::Idle:
                break;

            case State::SendCmd:
                serial.print(F("AT+CIPSEND="));
                serial.print(linkId);
                serial.print(F(","));
                serial.println(payloadLen);
                timerStart = currentMs;
                prevRxByte = 0;
                state = State::WaitPrompt;
                break;

            case State::WaitPrompt:
                while (serial.available()) {
                    uint8_t b = serial.read();
                    if (prevRxByte == '>' && b == ' ') {
                        state = State::PumpPayload;
                        break;
                    }
                    prevRxByte = b;
                }
                if (state != State::PumpPayload && (currentMs - timerStart > 1000)) {
                    state = State::ErrorRecovery;
                }
                break;

            case State::PumpPayload:
                serial.write(payload, payloadLen);
                timerStart = currentMs;
                state = State::WaitResult;
                break;

            case State::WaitResult:
                // Перевірка відповідей SEND OK у головному циклі
                if (currentMs - timerStart > 5000) {
                    state = State::ErrorRecovery;
                }
                break;

            case State::ErrorRecovery:
                serial.println(); // Скидання очікування команд
                state = State::Idle;
                break;
        }
    }

    State getState() const { return state; }
};
