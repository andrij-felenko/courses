#include <Arduino.h>

enum AtResponseStatus {
    AT_RESP_OK,
    AT_RESP_ERROR,
    AT_RESP_BUSY,
    AT_RESP_UNKNOWN
};

AtResponseStatus parseAtResponse(const String& line) {
    if (line.indexOf("OK") != -1) {
        return AT_RESP_OK;
    } else if (line.indexOf("ERROR") != -1) {
        return AT_RESP_ERROR;
    } else if (line.indexOf("BUSY") != -1) {
        return AT_RESP_BUSY;
    }
    return AT_RESP_UNKNOWN;
}
