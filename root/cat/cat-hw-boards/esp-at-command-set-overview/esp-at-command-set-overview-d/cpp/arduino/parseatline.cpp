// Класифікація вхідних рядків ESP-AT на хост-мікроконтролері (C++ / Arduino)
#include <Arduino.h>

enum AtResponseType {
    RESP_UNKNOWN,
    RESP_OK,
    RESP_ERROR,
    RESP_BUSY,
    RESP_URC,
    RESP_DATA
};

AtResponseType parseAtLine(const String &line) {
    if (line == "OK") {
        return RESP_OK;
    } else if (line == "ERROR" || line.startsWith("+CME ERROR:")) {
        return RESP_ERROR;
    } else if (line.startsWith("BUSY") || line.startsWith("busy")) {
        return RESP_BUSY;
    } else if (line.startsWith("WIFI ") || line.startsWith("+IPD") || line == "ready") {
        return RESP_URC;
    } else if (line.startsWith("+")) {
        return RESP_DATA;
    }
    return RESP_UNKNOWN;
}
