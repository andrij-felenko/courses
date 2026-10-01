#include <stdio.h>
#include <string.h>
#include <stdbool.h>

typedef enum {
    AT_STATE_IDLE,
    AT_STATE_WAIT_LINE,
    AT_STATE_SUCCESS,
    AT_STATE_ERROR,
    AT_STATE_TIMEOUT
} at_parser_state_t;

at_parser_state_t parse_at_response(const char *buffer, unsigned int timeout_ms) {
    at_parser_state_t state = AT_STATE_WAIT_LINE;
    
    if (strstr(buffer, "\r\nOK\r\n") != NULL) {
        state = AT_STATE_SUCCESS;
    } else if (strstr(buffer, "\r\nERROR\r\n") != NULL || strstr(buffer, "FAIL") != NULL) {
        state = AT_STATE_ERROR;
    } else if (timeout_ms == 0) {
        state = AT_STATE_TIMEOUT;
    }
    
    return state;
}
