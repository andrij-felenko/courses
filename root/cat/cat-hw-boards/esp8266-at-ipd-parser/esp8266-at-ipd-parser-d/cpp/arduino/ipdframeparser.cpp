#include <Arduino.h>

class IpdFrameParser {
public:
    enum State { IDLE, PREFIX, LINK_ID, LEN, PAYLOAD };

    IpdFrameParser(bool isMux = false) : state(IDLE), linkId(0), payloadLen(0), readBytes(0), mux(isMux) {}

    void reset() {
        state = IDLE;
        linkId = 0;
        payloadLen = 0;
        readBytes = 0;
    }

    void processByte(uint8_t byte) {
        char c = static_cast<char>(byte);
        switch (state) {
            case IDLE:
                if (c == '+') state = PREFIX;
                break;
            case PREFIX:
                if (c == ',') {
                    state = mux ? LINK_ID : LEN;
                    payloadLen = 0;
                    linkId = 0;
                }
                break;
            case LINK_ID:
                if (c >= '0' && c <= '9') {
                    linkId = c - '0';
                } else if (c == ',') {
                    state = LEN;
                    payloadLen = 0;
                }
                break;
            case LEN:
                if (c >= '0' && c <= '9') {
                    payloadLen = payloadLen * 10 + (c - '0');
                } else if (c == ':') {
                    state = PAYLOAD;
                    readBytes = 0;
                }
                break;
            case PAYLOAD:
                readBytes++;
                if (readBytes >= payloadLen) {
                    state = IDLE;
                }
                break;
        }
    }

    State getState() const { return state; }
    uint16_t getLen() const { return payloadLen; }
    uint8_t getLinkId() const { return linkId; }

private:
    State state;
    uint8_t linkId;
    uint16_t payloadLen;
    uint16_t readBytes;
    bool mux;
};
