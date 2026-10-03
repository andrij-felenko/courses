#include <Arduino.h>

enum class AtState {
    Idle,
    WaitPrompt,
    Streaming,
    WaitOk
};

class AtSocketDriver {
private:
    AtState state = AtState::Idle;
    unsigned long lastByteTimeMs = 0;
    bool promptReceived = false;

public:
    void feedByte(uint8_t b) {
        lastByteTimeMs = millis();
        if (state == AtState::WaitPrompt && b == '>') {
            promptReceived = true;
            state = AtState::Streaming;
        }
    }

    bool preparePassthroughSend(Stream& uart) {
        state = AtState::WaitPrompt;
        promptReceived = false;
        uart.print("AT+CIPSEND\r\n");
        return true;
    }

    bool exitPassthrough(Stream& uart) {
        if (millis() - lastByteTimeMs < 1000) {
            return false; // Необхідно зачекати 1000 мс тиші на лінії
        }
        uart.print("+++");
        delay(1050); // Захисний інтервал після +++
        state = AtState::WaitOk;
        return true;
    }

    AtState getState() const { return state; }
};
