#include <Arduino.h>

class SafeIpdRingParser {
public:
    static constexpr size_t RING_SIZE = 1024;
    static constexpr size_t MAX_PAYLOAD = 1460;
    static constexpr uint32_t TIMEOUT_LIMIT_MS = 100;

    enum class State { Idle, Prefix, LinkId, Len, Payload };

    SafeIpdRingParser(bool multilink) : isMultilink(multilink) { reset(); }

    void reset() {
        state = State::Idle;
        prefixIdx = 0;
        linkId = 0;
        payloadLen = 0;
        bytesRead = 0;
        lastTimeMs = millis();
    }

    void feedChar(char c) {
        lastTimeMs = millis();
        switch (state) {
            case State::Idle:
                if (c == '+') { state = State::Prefix; prefixIdx = 0; }
                break;
            case State::Prefix:
                if ("IPD,"[prefixIdx] == c) {
                    prefixIdx++;
                    if (prefixIdx == 4) {
                        state = isMultilink ? State::LinkId : State::Len;
                        payloadLen = 0;
                        linkId = 0;
                    }
                } else {
                    state = State::Idle;
                }
                break;
            case State::LinkId:
                if (c >= '0' && c <= '9') {
                    linkId = linkId * 10 + (c - '0');
                } else if (c == ',') {
                    state = State::Len;
                } else {
                    state = State::Idle;
                }
                break;
            case State::Len:
                if (c >= '0' && c <= '9') {
                    payloadLen = payloadLen * 10 + (c - '0');
                } else if (c == ':') {
                    bytesRead = 0;
                    state = (payloadLen > 0) ? State::Payload : State::Idle;
                } else {
                    state = State::Idle;
                }
                break;
            case State::Payload:
                if (bytesRead < MAX_PAYLOAD) {
                    payloadBuffer[bytesRead++] = static_cast<uint8_t>(c);
                }
                if (bytesRead >= payloadLen) {
                    onFrameComplete(linkId, payloadBuffer, bytesRead);
                    state = State::Idle;
                }
                break;
        }
    }

    void updateTimeout() {
        if (state != State::Idle && (millis() - lastTimeMs > TIMEOUT_LIMIT_MS)) {
            reset();
        }
    }

protected:
    virtual void onFrameComplete(uint8_t link, const uint8_t* data, size_t len) {
        // Перевизначається у похідному класі для обробки кадру
    }

private:
    State state;
    size_t prefixIdx;
    uint8_t linkId;
    size_t payloadLen;
    size_t bytesRead;
    uint32_t lastTimeMs;
    bool isMultilink;
    uint8_t payloadBuffer[MAX_PAYLOAD];
};
