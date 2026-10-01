enum class ParserState {
    Idle,
    MatchPrefix,
    ParseLen,
    ReadPayload
};

class IpdParser {
private:
    ParserState state = ParserState::Idle;
    uint16_t payloadLen = 0;
    uint16_t rxCount = 0;

public:
    void processByte(uint8_t b) {
        switch (state) {
            case ParserState::Idle:
                if (b == '+') state = ParserState::MatchPrefix;
                break;
            case ParserState::MatchPrefix:
                state = ParserState::ParseLen;
                payloadLen = 0;
                break;
            case ParserState::ParseLen:
                if (b >= '0' && b <= '9') {
                    payloadLen = payloadLen * 10 + (b - '0');
                } else if (b == ':') {
                    rxCount = 0;
                    state = ParserState::ReadPayload;
                }
                break;
            case ParserState::ReadPayload:
                rxCount++;
                if (rxCount >= payloadLen) {
                    state = ParserState::Idle;
                }
                break;
        }
    }
};
