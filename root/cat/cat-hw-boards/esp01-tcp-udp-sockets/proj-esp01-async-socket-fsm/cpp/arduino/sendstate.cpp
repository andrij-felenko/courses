#include <Arduino.h>

enum class SendState {
    Idle,
    WaitPrompt,
    Transmitting,
    WaitAck,
    Success,
    Failed
};

class SendFsm {
public:
    SendState state = SendState::Idle;
    uint32_t timerMs = 0;
    uint8_t linkId = 0;
    const uint8_t* txData = nullptr;
    uint16_t txLen = 0;

    void startSend(uint8_t id, const uint8_t* data, uint16_t len, uint32_t now) {
        linkId = id;
        txData = data;
        txLen = len;
        state = SendState::WaitPrompt;
        timerMs = now;
    }

    void poll(uint32_t now) {
        if (state == SendState::WaitPrompt && (now - timerMs > 2000)) {
            state = SendState::Failed;
        } else if (state == SendState::WaitAck && (now - timerMs > 5000)) {
            state = SendState::Failed;
        }
    }

    void handleRxChar(char c, uint32_t now, Print& serialOut) {
        if (state == SendState::WaitPrompt && c == '>') {
            state = SendState::Transmitting;
            serialOut.write(txData, txLen);
            state = SendState::WaitAck;
            timerMs = now;
        }
    }

    void handleLine(const String& line) {
        if (state == SendState::WaitAck) {
            if (line.indexOf("SEND OK") >= 0) {
                state = SendState::Success;
            } else if (line.indexOf("SEND FAIL") >= 0 || line.indexOf("ERROR") >= 0) {
                state = SendState::Failed;
            }
        }
    }
};
