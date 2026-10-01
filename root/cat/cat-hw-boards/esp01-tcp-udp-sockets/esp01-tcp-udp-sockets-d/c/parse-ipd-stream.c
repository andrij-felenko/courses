#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef enum {
    PARSE_SEARCH_PREFIX,
    PARSE_READ_HEADER,
    PARSE_READ_PAYLOAD
} parse_state_t;

void parse_ipd_stream(const char *buffer, size_t buf_len) {
    static parse_state_t state = PARSE_SEARCH_PREFIX;
    static int payload_len = 0;
    static int bytes_read = 0;
    static char header_buf[32];
    static int header_idx = 0;

    for (size_t i = 0; i < buf_len; i++) {
        char c = buffer[i];
        if (state == PARSE_SEARCH_PREFIX) {
            if (c == '+') {
                header_idx = 0;
                header_buf[header_idx++] = c;
                state = PARSE_READ_HEADER;
            }
        } else if (state == PARSE_READ_HEADER) {
            if (header_idx < sizeof(header_buf) - 1) {
                header_buf[header_idx++] = c;
            }
            if (c == ':') {
                header_buf[header_idx] = '\0';
                char *last_comma = strrchr(header_buf, ',');
                if (last_comma != NULL) {
                    payload_len = atoi(last_comma + 1);
                }
                bytes_read = 0;
                state = (payload_len > 0) ? PARSE_READ_PAYLOAD : PARSE_SEARCH_PREFIX;
            }
        } else if (state == PARSE_READ_PAYLOAD) {
            bytes_read++;
            if (bytes_read >= payload_len) {
                state = PARSE_SEARCH_PREFIX;
            }
        }
    }
}
