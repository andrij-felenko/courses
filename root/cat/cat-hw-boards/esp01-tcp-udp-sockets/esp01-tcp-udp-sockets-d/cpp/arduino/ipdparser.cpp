#include <Arduino.h>

class IpdParser {
public:
    enum State {
        IDLE,
        MATCH_PREFIX,
        READ_LINK_ID,
        READ_LENGTH,
        READ_PAYLOAD
    };

    static const uint16_t MAX_PAYLOAD = 512;

    IpdParser() { reset(); }

    void reset() {
        m_state = IDLE;
        m_linkId = 0;
        m_payloadLen = 0;
        m_bytesRead = 0;
        m_prefixIdx = 0;
    }

    bool feed(uint8_t byte, bool isMux = false) {
        switch (m_state) {
        case IDLE:
            if (byte == '+') {
                m_prefixIdx = 1;
                m_state = MATCH_PREFIX;
            }
            break;

        case MATCH_PREFIX:
            if (byte == m_prefix[m_prefixIdx]) {
                m_prefixIdx++;
                if (m_prefixIdx == 5) {
                    if (isMux) {
                        m_linkId = 0;
                        m_state = READ_LINK_ID;
                    } else {
                        m_payloadLen = 0;
                        m_state = READ_LENGTH;
                    }
                }
            } else {
                m_state = IDLE;
            }
            break;

        case READ_LINK_ID:
            if (byte >= '0' && byte <= '9') {
                m_linkId = byte - '0';
            } else if (byte == ',') {
                m_payloadLen = 0;
                m_state = READ_LENGTH;
            } else {
                m_state = IDLE;
            }
            break;

        case READ_LENGTH:
            if (byte >= '0' && byte <= '9') {
                m_payloadLen = (m_payloadLen * 10) + (byte - '0');
            } else if (byte == ':') {
                m_bytesRead = 0;
                if (m_payloadLen > 0 && m_payloadLen <= MAX_PAYLOAD) {
                    m_state = READ_PAYLOAD;
                } else {
                    m_state = IDLE;
                }
            } else {
                m_state = IDLE;
            }
            break;

        case READ_PAYLOAD:
            m_payload[m_bytesRead++] = byte;
            if (m_bytesRead == m_payloadLen) {
                m_state = IDLE;
                return true; // Кадр успішно зібрано
            }
            break;
        }
        return false;
    }

    uint8_t getLinkId() const { return m_linkId; }
    uint16_t getPayloadLength() const { return m_payloadLen; }
    const uint8_t* getPayload() const { return m_payload; }

private:
    State m_state;
    uint8_t m_linkId;
    uint16_t m_payloadLen;
    uint16_t m_bytesRead;
    uint8_t m_prefixIdx;
    const char* m_prefix = "+IPD,";
    uint8_t m_payload[MAX_PAYLOAD];
};
