// Потоковий парсер кадрів +IPD мовою C++
#include <Arduino.h>

class IpdParser {
private:
    enum State { SEARCH, PARSE_ID, PARSE_LEN, READ_DATA } state = SEARCH;
    char history[5] = {0};
    int linkId = 0;
    int payloadLen = 0;
    int bytesRead = 0;
    bool multiLink;

public:
    IpdParser(bool isMulti) : multiLink(isMulti) {}

    void processByte(uint8_t b) {
        switch (state) {
            case SEARCH:
                memmove(history, history + 1, 4);
                history[4] = b;
                if (memcmp(history, "+IPD,", 5) == 0) {
                    linkId = 0; payloadLen = 0; bytesRead = 0;
                    state = multiLink ? PARSE_ID : PARSE_LEN;
                }
                break;
            case PARSE_ID:
                if (b >= '0' && b <= '9') linkId = b - '0';
                else if (b == ',') state = PARSE_LEN;
                break;
            case PARSE_LEN:
                if (b >= '0' && b <= '9') payloadLen = payloadLen * 10 + (b - '0');
                else if (b == ':') state = READ_DATA;
                break;
            case READ_DATA:
                bytesRead++;
                if (bytesRead >= payloadLen) state = SEARCH;
                break;
        }
    }
};
