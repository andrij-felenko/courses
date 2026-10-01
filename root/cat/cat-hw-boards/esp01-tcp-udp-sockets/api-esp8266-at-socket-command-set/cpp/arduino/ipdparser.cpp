#include <Arduino.h>

enum IpdState {
    SEARCH_IPD,
    READ_LINK_ID,
    READ_LENGTH,
    READ_PAYLOAD
};

class IpdParser {
private:
    IpdState state = SEARCH_IPD;
    uint8_t linkId = 0;
    uint16_t payloadLen = 0;
    uint16_t bytesRead = 0;
    uint8_t matchIdx = 0;
    uint8_t buffer[1024];

public:
    void processByte(uint8_t c) {
        const char pattern[] = "+IPD,";
        switch (state) {
            case SEARCH_IPD:
                if (c == pattern[matchIdx]) {
                    matchIdx++;
                    if (matchIdx == 5) {
                        state = READ_LINK_ID;
                        linkId = 0;
                        payloadLen = 0;
                        matchIdx = 0;
                    }
                } else {
                    matchIdx = (c == pattern[0]) ? 1 : 0;
                }
                break;

            case READ_LINK_ID:
                if (c >= '0' && c <= '4') {
                    linkId = c - '0';
                } else if (c == ',') {
                    state = READ_LENGTH;
                }
                break;

            case READ_LENGTH:
                if (c >= '0' && c <= '9') {
                    payloadLen = payloadLen * 10 + (c - '0');
                } else if (c == ':') {
                    bytesRead = 0;
                    state = (payloadLen > 0) ? READ_PAYLOAD : SEARCH_IPD;
                }
                break;

            case READ_PAYLOAD:
                if (bytesRead < sizeof(buffer)) {
                    buffer[bytesRead] = c;
                }
                bytesRead++;
                if (bytesRead >= payloadLen) {
                    // Корисне навантаження прийнято повністю
                    state = SEARCH_IPD;
                }
                break;
        }
    }
};
