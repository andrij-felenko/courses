#include <stdio.h>
#include <string.h>
#include <stdbool.h>

// Типи статусних відповідей та подій ESP8266
typedef enum {
    AT_RESP_SEARCHING,
    AT_RESP_OK,
    AT_RESP_ERROR,
    AT_RESP_FAIL,
    AT_RESP_BUSY,
    AT_RESP_URC
} at_response_type_t;

// Класифікація вхідного рядка від ESP8266
at_response_type_t parse_at_line(const char *line) {
    if (strcmp(line, "OK\r\n") == 0 || strcmp(line, "OK") == 0) {
        return AT_RESP_OK;
    }
    if (strcmp(line, "ERROR\r\n") == 0 || strcmp(line, "ERROR") == 0) {
        return AT_RESP_ERROR;
    }
    if (strcmp(line, "FAIL\r\n") == 0 || strcmp(line, "FAIL") == 0) {
        return AT_RESP_FAIL;
    }
    if (strncmp(line, "busy", 4) == 0 || strncmp(line, "BUSY", 4) == 0) {
        return AT_RESP_BUSY;
    }
    
    // Перевірка на асинхронні сповіщення URC
    if (strncmp(line, "WIFI ", 5) == 0 || 
        strncmp(line, "ready", 5) == 0 || 
        strncmp(line, "+IPD,", 5) == 0) {
        return AT_RESP_URC;
    }
    
    return AT_RESP_SEARCHING; // Інформаційне тіло команди (Payload)
}
