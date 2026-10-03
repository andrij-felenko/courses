#include <Arduino.h>

enum class SendStatusResult {
    Waiting,
    RecvHeader,
    SendOk,
    SendFail,
    Error,
    Busy
};

SendStatusResult parseCipsendResponseLine(const String& line) {
    if (line.indexOf("SEND OK") != -1) {
        return SendStatusResult::SendOk;
    }
    if (line.indexOf("SEND FAIL") != -1) {
        return SendStatusResult::SendFail;
    }
    if (line.indexOf("ERROR") != -1) {
        return SendStatusResult::Error;
    }
    if (line.indexOf("busy s...") != -1 || line.indexOf("busy p...") != -1) {
        return SendStatusResult::Busy;
    }
    if (line.indexOf("Recv ") != -1 && line.indexOf("bytes") != -1) {
        return SendStatusResult::RecvHeader;
    }
    return SendStatusResult::Waiting;
}
