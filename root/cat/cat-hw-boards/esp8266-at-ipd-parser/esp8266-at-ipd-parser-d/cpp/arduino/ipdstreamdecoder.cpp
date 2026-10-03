#include <Arduino.h>

class IpdStreamDecoder {
public:
    using PayloadCallback = void (*)(uint8_t linkId, const uint8_t *payload, uint16_t length);

    enum class State {
        Idle,
        Prefix,
        LinkId,
        Length,
        Payload,
        Done
    };

    IpdStreamDecoder(bool multilink = false, uint16_t maxLen = 1024)
        : currentState(State::Idle), prefixIndex(0), linkId(0),
          payloadLength(0), bytesRead(0), isMultilink(multilink),
          maxBufferLength(maxLen), onPayloadReceived(nullptr) {
        buffer = new uint8_t[maxBufferLength];
    }

    ~IpdStreamDecoder() {
        delete[] buffer;
    }

    void setCallback(PayloadCallback cb) {
        onPayloadReceived = cb;
    }

    void reset() {
        currentState = State::Idle;
        prefixIndex = 0;
        linkId = 0;
        payloadLength = 0;
        bytesRead = 0;
    }

    void processByte(uint8_t byte) {
        char c = static_cast<char>(byte);

        switch (currentState) {
            case State::Idle:
                if (c == '+') {
                    currentState = State::Prefix;
                    prefixIndex = 0;
                }
                break;

            case State::Prefix:
                if (c == PREFIX[prefixIndex]) {
                    prefixIndex++;
                    if (PREFIX[prefixIndex] == '\0') {
                        payloadLength = 0;
                        linkId = 0;
                        currentState = isMultilink ? State::LinkId : State::Length;
                    }
                } else {
                    reset();
                }
                break;

            case State::LinkId:
                if (c >= '0' && c <= '9') {
                    linkId = c - '0';
                } else if (c == ',') {
                    currentState = State::Length;
                    payloadLength = 0;
                } else {
                    reset();
                }
                break;

            case State::Length:
                if (c >= '0' && c <= '9') {
                    payloadLength = payloadLength * 10 + (c - '0');
                    if (payloadLength > maxBufferLength) {
                        reset();
                    }
                } else if (c == ':') {
                    if (payloadLength > 0) {
                        currentState = State::Payload;
                        bytesRead = 0;
                    } else {
                        if (onPayloadReceived) {
                            onPayloadReceived(linkId, buffer, 0);
                        }
                        reset();
                    }
                } else {
                    reset();
                }
                break;

            case State::Payload:
                buffer[bytesRead++] = byte;
                if (bytesRead >= payloadLength) {
                    currentState = State::Done;
                    if (onPayloadReceived) {
                        onPayloadReceived(linkId, buffer, payloadLength);
                    }
                    reset();
                }
                break;

            case State::Done:
                reset();
                break;
        }
    }

private:
    static constexpr const char* PREFIX = "IPD,";
    State currentState;
    uint8_t prefixIndex;
    uint8_t linkId;
    uint16_t payloadLength;
    uint16_t bytesRead;
    bool isMultilink;
    uint16_t maxBufferLength;
    uint8_t *buffer;
    PayloadCallback onPayloadReceived;
};
