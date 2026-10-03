#include <Arduino.h>

enum class IpdState {
    SearchPrefix,
    ParseLinkId,
    ParseLen,
    StreamPayload
};

class IpdStreamParser {
private:
    IpdState state = IpdState::SearchPrefix;
    uint8_t matchIdx = 0;
    uint8_t linkId = 0;
    uint16_t bytesRemaining = 0;
    const char* prefix = "+IPD,";

public:
    void reset() {
        state = IpdState::SearchPrefix;
        matchIdx = 0;
        linkId = 0;
        bytesRemaining = 0;
    }

    bool processByte(uint8_t b, void (*payloadHandler)(uint8_t id, uint8_t data)) {
        switch (state) {
            case IpdState::SearchPrefix:
                if (b == (uint8_t)prefix[matchIdx]) {
                    matchIdx++;
                    if (prefix[matchIdx] == '\0') {
                        state = IpdState::ParseLinkId;
                        linkId = 0;
                        matchIdx = 0;
                    }
                } else {
                    matchIdx = (b == (uint8_t)prefix[0]) ? 1 : 0;
                }
                break;

            case IpdState::ParseLinkId:
                if (b >= '0' && b <= '9') {
                    linkId = linkId * 10 + (b - '0');
                } else if (b == ',') {
                    state = IpdState::ParseLen;
                    bytesRemaining = 0;
                } else {
                    state = IpdState::SearchPrefix;
                }
                break;

            case IpdState::ParseLen:
                if (b >= '0' && b <= '9') {
                    bytesRemaining = bytesRemaining * 10 + (b - '0');
                } else if (b == ':') {
                    if (bytesRemaining > 0) {
                        state = IpdState::StreamPayload;
                    } else {
                        state = IpdState::SearchPrefix;
                    }
                } else {
                    state = IpdState::SearchPrefix;
                }
                break;

            case IpdState::StreamPayload:
                if (payloadHandler) {
                    payloadHandler(linkId, b);
                }
                bytesRemaining--;
                if (bytesRemaining == 0) {
                    state = IpdState::SearchPrefix;
                }
                return true;
        }
        return false;
    }
};
