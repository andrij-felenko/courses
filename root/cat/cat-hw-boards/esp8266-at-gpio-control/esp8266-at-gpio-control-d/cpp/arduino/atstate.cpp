#include <Arduino.h>

enum class AtState {
    Idle,
    WaitLine,
    Success,
    Error,
    Timeout
};

AtState parseAtResponse(const String &buffer, uint32_t timeoutMs) {
    if (buffer.indexOf("\r\nOK\r\n") != -1) {
        return AtState::Success;
    }
    if (buffer.indexOf("\r\nERROR\r\n") != -1 || buffer.indexOf("FAIL") != -1) {
        return AtState::Error;
    }
    if (timeoutMs == 0) {
        return AtState::Timeout;
    }
    return AtState::WaitLine;
}
