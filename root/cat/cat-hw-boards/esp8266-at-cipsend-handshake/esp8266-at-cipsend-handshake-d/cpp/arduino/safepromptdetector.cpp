#include <Arduino.h>

class SafePromptDetector {
private:
    enum class State { SearchPrompt, SkipIpdBody };
    State state = State::SearchPrompt;
    uint16_t ipdBytesLeft = 0;
    uint8_t prevByte = 0;

public:
    void reset() {
        state = State::SearchPrompt;
        ipdBytesLeft = 0;
        prevByte = 0;
    }

    bool processByte(uint8_t byte) {
        if (state == State::SkipIpdBody) {
            if (--ipdBytesLeft == 0) {
                state = State::SearchPrompt;
            }
            prevByte = byte;
            return false;
        }

        if (prevByte == '>' && byte == ' ') {
            prevByte = 0;
            return true;
        }

        prevByte = byte;
        return false;
    }
};
