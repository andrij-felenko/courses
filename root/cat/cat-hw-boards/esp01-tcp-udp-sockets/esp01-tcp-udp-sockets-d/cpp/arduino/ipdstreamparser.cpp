#include <Arduino.h>

class IpdStreamParser {
public:
    enum State { IDLE, PREFIX, LINK_ID, LENGTH, BODY };

    IpdStreamParser(bool multiConn = false) 
        : _state(IDLE), _prefixIdx(0), _linkId(0), _length(0), _read(0), _multiConn(multiConn) {}

    void processByte(uint8_t b) {
        switch (_state) {
        case IDLE:
            if (b == '+') { _prefixIdx = 1; _state = PREFIX; }
            break;

        case PREFIX:
            if (b == "+IPD,"[_prefixIdx]) {
                _prefixIdx++;
                if (_prefixIdx == 5) {
                    if (_multiConn) { _linkId = 0; _state = LINK_ID; }
                    else { _linkId = 0; _length = 0; _state = LENGTH; }
                }
            } else { _state = IDLE; }
            break;

        case LINK_ID:
            if (b >= '0' && b <= '4') { _linkId = b - '0'; }
            else if (b == ',') { _length = 0; _state = LENGTH; }
            else { _state = IDLE; }
            break;

        case LENGTH:
            if (b >= '0' && b <= '9') { _length = _length * 10 + (b - '0'); }
            else if (b == ':') {
                _read = 0;
                _state = (_length > 0) ? BODY : IDLE;
            } else { _state = IDLE; }
            break;

        case BODY:
            onByteReceived(_linkId, b);
            _read++;
            if (_read >= _length) { _state = IDLE; }
            break;
        }
    }

protected:
    virtual void onByteReceived(uint8_t linkId, uint8_t b) = 0;

private:
    State _state;
    uint8_t _prefixIdx;
    uint8_t _linkId;
    uint16_t _length;
    uint16_t _read;
    bool _multiConn;
};
