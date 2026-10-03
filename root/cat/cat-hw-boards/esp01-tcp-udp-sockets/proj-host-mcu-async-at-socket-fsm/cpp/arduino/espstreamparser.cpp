#include <Arduino.h>

class EspStreamParser {
public:
    enum State { STATE_LINE, STATE_IPD_PAYLOAD };
    enum EventType { EVENT_NONE, EVENT_OK, EVENT_ERROR, EVENT_SEND_OK, EVENT_IPD };

    struct Event {
        EventType type;
        uint8_t linkId;
        uint16_t length;
        uint8_t payload[256];
    };

    EspStreamParser() : m_state(STATE_LINE), m_linePos(0), m_ipdLen(0), m_ipdReceived(0), m_linkId(0) {}

    bool processChar(char c, Event& outEvent) {
        outEvent.type = EVENT_NONE;

        if (m_state == STATE_IPD_PAYLOAD) {
            if (m_ipdReceived < sizeof(outEvent.payload)) {
                m_ipdBuffer[m_ipdReceived] = (uint8_t)c;
            }
            m_ipdReceived++;

            if (m_ipdReceived >= m_ipdLen) {
                outEvent.type = EVENT_IPD;
                outEvent.linkId = m_linkId;
                outEvent.length = (m_ipdReceived < sizeof(outEvent.payload)) ? m_ipdReceived : sizeof(outEvent.payload);
                memcpy(outEvent.payload, m_ipdBuffer, outEvent.length);
                
                m_state = STATE_LINE;
                m_linePos = 0;
                return true;
            }
            return false;
        }

        if (c == '\r') return false;

        if (c == '\n') {
            m_lineBuf[m_linePos] = '\0';
            if (strcmp(m_lineBuf, "OK") == 0) outEvent.type = EVENT_OK;
            else if (strcmp(m_lineBuf, "ERROR") == 0) outEvent.type = EVENT_ERROR;
            else if (strcmp(m_lineBuf, "SEND OK") == 0) outEvent.type = EVENT_SEND_OK;

            m_linePos = 0;
            return (outEvent.type != EVENT_NONE);
        }

        if (m_linePos < sizeof(m_lineBuf) - 1) {
            m_lineBuf[m_linePos++] = c;
            m_lineBuf[m_linePos] = '\0';
        } else {
            m_linePos = 0;
        }

        if (strncmp(m_lineBuf, "+IPD,", 5) == 0 && c == ':') {
            int link = 0, len = 0;
            if (sscanf(m_lineBuf, "+IPD,%d,%d:", &link, &len) == 2) {
                m_linkId = (uint8_t)link;
                m_ipdLen = (uint16_t)len;
            } else if (sscanf(m_lineBuf, "+IPD,%d:", &len) == 1) {
                m_linkId = 0;
                m_ipdLen = (uint16_t)len;
            }
            m_ipdReceived = 0;
            m_state = STATE_IPD_PAYLOAD;
            m_linePos = 0;
        }

        return false;
    }

private:
    State m_state;
    char m_lineBuf[128];
    size_t m_linePos;
    uint8_t m_ipdBuffer[256];
    uint16_t m_ipdLen;
    uint16_t m_ipdReceived;
    uint8_t m_linkId;
};
