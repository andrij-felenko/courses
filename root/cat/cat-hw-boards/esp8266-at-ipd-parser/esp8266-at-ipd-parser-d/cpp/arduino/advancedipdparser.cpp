#include <Arduino.h>

class AdvancedIpdParser {
public:
    enum class State { Idle, Prefix, LinkId, Len, SkipInfo, Payload };

    AdvancedIpdParser(bool multilink, bool cipdinfo)
        : isMultilink(multilink), hasCipdInfo(cipdinfo) {
        reset();
    }

    void reset() {
        state = State::Idle;
        prefixIdx = 0;
        linkId = 0;
        payloadLen = 0;
        bytesRead = 0;
    }

    void parseByte(uint8_t b) {
        char c = static_cast<char>(b);

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
                } else if (c == ',' && hasCipdInfo) {
                    state = State::SkipInfo;
                } else if (c == ':') {
                    bytesRead = 0;
                    state = (payloadLen == 0) ? State::Idle : State::Payload;
                } else {
                    state = State::Idle;
                }
                break;

            case State::SkipInfo:
                if (c == ':') {
                    bytesRead = 0;
                    state = (payloadLen == 0) ? State::Idle : State::Payload;
                }
                break;

            case State::Payload:
                if (bytesRead < sizeof(buffer)) {
                    buffer[bytesRead++] = b;
                }
                if (bytesRead >= payloadLen) {
                    onPacket(linkId, buffer, bytesRead);
                    state = State::Idle;
                }
                break;
        }
    }

protected:
    virtual void onPacket(uint8_t link, const uint8_t* data, size_t size) {
        // Обробка законченого пакета в дійсному застосунку
    }

private:
    State state;
    size_t prefixIdx;
    uint8_t linkId;
    size_t payloadLen;
    size_t bytesRead;
    bool isMultilink;
    bool hasCipdInfo;
    uint8_t buffer[2048];
};
