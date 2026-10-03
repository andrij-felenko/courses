#include <Arduino.h>

class ESP01RingBuffer {
private:
    static const uint16_t BUFFER_SIZE = 256;
    uint8_t _buf[BUFFER_SIZE];
    volatile uint16_t _head = 0;
    volatile uint16_t _tail = 0;

public:
    bool push(uint8_t b) {
        uint16_t next = (_head + 1) % BUFFER_SIZE;
        if (next == _tail) return false;
        _buf[_head] = b;
        _head = next;
        return true;
    }

    bool pop(uint8_t &b) {
        if (_head == _tail) return false;
        b = _buf[_tail];
        _tail = (_tail + 1) % BUFFER_SIZE;
        return true;
    }
};

class ESP01AsyncDriver {
public:
    enum State { IDLE_SEARCH, PARSE_IPD_HEADER, READ_IPD_PAYLOAD };
    typedef void (*DataCallback)(uint8_t linkId, uint8_t byte);

private:
    State _state = IDLE_SEARCH;
    ESP01RingBuffer _rxRing;
    uint8_t _linkId = 0;
    uint16_t _bytesLeft = 0;
    String _headerBuf = "";
    DataCallback _onData = nullptr;

public:
    void setCallback(DataCallback cb) { _onData = cb; }

    void handleRxInterrupt(uint8_t b) {
        _rxRing.push(b);
    }

    void update() {
        uint8_t b;
        while (_rxRing.pop(b)) {
            switch (_state) {
                case IDLE_SEARCH:
                    _headerBuf += (char)b;
                    if (_headerBuf.endsWith("+IPD,")) {
                        _state = PARSE_IPD_HEADER;
                        _headerBuf = "";
                    } else if (_headerBuf.length() > 32) {
                        _headerBuf = _headerBuf.substring(_headerBuf.length() - 16);
                    }
                    break;

                case PARSE_IPD_HEADER:
                    if (b == ':') {
                        int commaIdx = _headerBuf.indexOf(',');
                        if (commaIdx >= 0) {
                            _linkId = _headerBuf.substring(0, commaIdx).toInt();
                            _bytesLeft = _headerBuf.substring(commaIdx + 1).toInt();
                        } else {
                            _linkId = 0;
                            _bytesLeft = _headerBuf.toInt();
                        }
                        _state = READ_IPD_PAYLOAD;
                    } else {
                        _headerBuf += (char)b;
                    }
                    break;

                case READ_IPD_PAYLOAD:
                    if (_onData) _onData(_linkId, b);
                    _bytesLeft--;
                    if (_bytesLeft == 0) {
                        _headerBuf = "";
                        _state = IDLE_SEARCH;
                    }
                    break;
            }
        }
    }
};
