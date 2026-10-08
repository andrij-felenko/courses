#include <stdio.h>
#include <string.h>

typedef enum {
    AT_RESP_OK,
    AT_RESP_ERROR,
    AT_RESP_BUSY,
    AT_RESP_TIMEOUT
} at_response_status_t;

at_response_status_t parse_at_response(const char* line) {
    if (strstr(line, "OK") != NULL) {
        return AT_RESP_OK;
    } else if (strstr(line, "ERROR") != NULL) {
        return AT_RESP_ERROR;
    } else if (strstr(line, "BUSY") != NULL) {
        return AT_RESP_BUSY;
    }
    return AT_RESP_TIMEOUT;
}
