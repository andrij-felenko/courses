#include <Arduino.h>

enum ParserState { SEARCH_PREFIX, PARSE_HEADER, READ_PAYLOAD };

class IpdParser {
private:
    ParserState state = SEARCH_PREFIX;
    uint16_t payloadLen = 0;
    uint16_t bytesRead = 0;
    uint8_t buffer[512];

public:
    void processByte(uint8_t b) {
        switch (state) {
            case SEARCH_PREFIX:
                // Перевірка входження підрядка "+IPD,"
                break;
            case PARSE_HEADER:
                if (b >= '0' && b <= '9') {
                    payloadLen = payloadLen * 10 + (b - '0');
                } else if (b == ':') {
                    bytesRead = 0;
                    state = READ_PAYLOAD;
                }
                break;
            case READ_PAYLOAD:
                buffer[bytesRead++] = b;
                if (bytesRead >= payloadLen) {
                    // Корисна передача завершена
                    state = SEARCH_PREFIX;
                }
                break;
        }
    }
};
