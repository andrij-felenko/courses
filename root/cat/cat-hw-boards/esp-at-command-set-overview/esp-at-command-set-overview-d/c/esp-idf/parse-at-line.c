// Класифікація вхідних рядків ESP-AT на хост-мікроконтролері (C / ESP-IDF)
#include <stdio.h>
#include <string.h>
#include <stdbool.h>

typedef enum {
    AT_RESP_UNKNOWN,
    AT_RESP_OK,
    AT_RESP_ERROR,
    AT_RESP_BUSY,
    AT_RESP_URC,
    AT_RESP_DATA
} at_response_type_t;

// Аналіз отриманого рядка, кадрованого \r\n
at_response_type_t parse_at_line(const char *line) {
    if (strcmp(line, "OK") == 0) {
        return AT_RESP_OK;
    } else if (strcmp(line, "ERROR") == 0 || strncmp(line, "+CME ERROR:", 11) == 0) {
        return AT_RESP_ERROR;
    } else if (strncmp(line, "BUSY", 4) == 0 || strncmp(line, "busy", 4) == 0) {
        return AT_RESP_BUSY;
    } else if (strncmp(line, "WIFI ", 5) == 0 || strncmp(line, "+IPD", 4) == 0 || strcmp(line, "ready") == 0) {
        return AT_RESP_URC;
    } else if (line[0] == '+') {
        return AT_RESP_DATA;
    }
    return AT_RESP_UNKNOWN;
}
