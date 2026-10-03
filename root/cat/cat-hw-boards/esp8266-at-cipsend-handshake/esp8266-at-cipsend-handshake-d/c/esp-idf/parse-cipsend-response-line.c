#include <stdio.h>
#include <string.h>
#include <stdbool.h>

typedef enum {
    SEND_STATUS_WAITING,
    SEND_STATUS_RECV_HEADER,
    SEND_STATUS_OK,
    SEND_STATUS_FAIL,
    SEND_STATUS_ERROR,
    SEND_STATUS_BUSY
} SendStatusResult;

SendStatusResult parse_cipsend_response_line(const char* line) {
    if (!line) return SEND_STATUS_WAITING;

    if (strstr(line, "SEND OK") != NULL) {
        return SEND_STATUS_OK;
    }
    if (strstr(line, "SEND FAIL") != NULL) {
        return SEND_STATUS_FAIL;
    }
    if (strstr(line, "ERROR") != NULL) {
        return SEND_STATUS_ERROR;
    }
    if (strstr(line, "busy s...") != NULL || strstr(line, "busy p...") != NULL) {
        return SEND_STATUS_BUSY;
    }
    if (strstr(line, "Recv ") != NULL && strstr(line, "bytes") != NULL) {
        return SEND_STATUS_RECV_HEADER; // Проміжний статус вичитання буфера
    }

    return SEND_STATUS_WAITING;
}
