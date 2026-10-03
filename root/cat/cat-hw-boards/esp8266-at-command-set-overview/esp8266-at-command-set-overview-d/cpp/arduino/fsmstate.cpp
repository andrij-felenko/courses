#include <Arduino.h>

constexpr size_t RING_BUFFER_CAPACITY = 576;
constexpr size_t MAX_LINE_LENGTH = 256;
constexpr uint32_t DEFAULT_TIMEOUT_MS = 2000;

enum class FsmState {
    Idle,
    Accumulating,
    Evaluate,
    Timeout,
    Error
};

enum class FsmResult {
    Busy,
    Ok,
    Error,
    Fail,
    Timeout,
    UrcDetected
};

class AtFsmParser {
private:
    uint8_t ringBuffer[RING_BUFFER_CAPACITY];
    size_t head = 0;
    size_t tail = 0;
    
    char lineBuffer[MAX_LINE_LENGTH];
    size_t lineIdx = 0;
    
    FsmState currentState = FsmState::Idle;
    uint32_t startTimeMs = 0;

public:
    AtFsmParser() = default;

    void pushByte(uint8_t b) {
        size_t next = (head + 1) % RING_BUFFER_CAPACITY;
        if (next != tail) { // Захист від переповнення
            ringBuffer[head] = b;
            head = next;
        }
    }

    bool popByte(uint8_t& b) {
        if (head == tail) return false;
        b = ringBuffer[tail];
        tail = (tail + 1) % RING_BUFFER_CAPACITY;
        return true;
    }

    void resync() {
        head = 0;
        tail = 0;
        lineIdx = 0;
        currentState = FsmState::Idle;
    }

    FsmResult process(uint32_t timeoutMs = DEFAULT_TIMEOUT_MS) {
        uint32_t now = millis();

        if (currentState != FsmState::Idle && (now - startTimeMs) > timeoutMs) {
            currentState = FsmState::Timeout;
            resync();
            return FsmResult::Timeout;
        }

        uint8_t b;
        while (popByte(b)) {
            if (currentState == FsmState::Idle) {
                currentState = FsmState::Accumulating;
                startTimeMs = now;
            }

            if (b == '\n') {
                if (lineIdx > 0 && lineBuffer[lineIdx - 1] == '\r') {
                    lineBuffer[lineIdx - 1] = '\0';
                } else {
                    lineBuffer[lineIdx] = '\0';
                }

                currentState = FsmState::Evaluate;
                String line = String(lineBuffer);

                if (line == "OK") {
                    resync();
                    return FsmResult::Ok;
                }
                if (line == "ERROR") {
                    resync();
                    return FsmResult::Error;
                }
                if (line == "FAIL") {
                    resync();
                    return FsmResult::Fail;
                }

                if (line.startsWith("WIFI ") || line == "ready" || line.startsWith("+IPD,")) {
                    lineIdx = 0;
                    currentState = FsmState::Accumulating;
                    return FsmResult::UrcDetected;
                }

                lineIdx = 0;
                currentState = FsmState::Accumulating;
            } else if (b != '\r') {
                if (lineIdx < MAX_LINE_LENGTH - 1) {
                    lineBuffer[lineIdx++] = static_cast<char>(b);
                } else {
                    resync();
                    return FsmResult::Error;
                }
            }
        }

        return FsmResult::Busy;
    }
};
