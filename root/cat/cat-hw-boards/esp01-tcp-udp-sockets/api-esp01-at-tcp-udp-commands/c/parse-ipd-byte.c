// Потоковий парсер кадрів +IPD мовою C
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

typedef enum {
    STATE_SEARCH,
    STATE_PARSE_LINK_ID,
    STATE_PARSE_LEN,
    STATE_READ_DATA
} ipd_state_t;

static ipd_state_t state = STATE_SEARCH;
static uint8_t ring_buf[5] = {0};
static int link_id = 0;
static int payload_len = 0;
static int bytes_read = 0;

void parse_ipd_byte(uint8_t byte, bool is_multilink) {
    switch (state) {
        case STATE_SEARCH:
            ring_buf[0] = ring_buf[1]; ring_buf[1] = ring_buf[2];
            ring_buf[2] = ring_buf[3]; ring_buf[3] = ring_buf[4];
            ring_buf[4] = byte;
            if (ring_buf[0]=='+' && ring_buf[1]=='I' && ring_buf[2]=='P' && ring_buf[3]=='D' && ring_buf[4]==',') {
                link_id = 0;
                payload_len = 0;
                bytes_read = 0;
                state = is_multilink ? STATE_PARSE_LINK_ID : STATE_PARSE_LEN;
            }
            break;

        case STATE_PARSE_LINK_ID:
            if (byte >= '0' && byte <= '9') {
                link_id = byte - '0';
            } else if (byte == ',') {
                state = STATE_PARSE_LEN;
            }
            break;

        case STATE_PARSE_LEN:
            if (byte >= '0' && byte <= '9') {
                payload_len = payload_len * 10 + (byte - '0');
            } else if (byte == ':') {
                state = STATE_READ_DATA;
            }
            break;

        case STATE_READ_DATA:
            // Збереження байта у цільовий буфер сокета
            bytes_read++;
            if (bytes_read >= payload_len) {
                state = STATE_SEARCH; // Кадр +IPD повністю прийнято
            }
            break;
    }
}
