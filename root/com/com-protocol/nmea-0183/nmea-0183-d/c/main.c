#include <stdint.h>
#include <stdbool.h>

typedef enum {
    FSM_WAIT_START,
    FSM_READ_PAYLOAD,
    FSM_READ_CS1,
    FSM_READ_CS2,
    FSM_WAIT_CR,
    FSM_WAIT_LF
} nmea_state_t;

typedef struct {
    nmea_state_t state;
    char buffer[84];
    uint8_t idx;
    uint8_t calc_crc;
    uint8_t rx_crc;
} nmea_fsm_t;

static inline int hex_val(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

bool nmea_fsm_feed(nmea_fsm_t *fsm, uint8_t byte) {
    if (byte == '$' || byte == '!') {
        fsm->state = FSM_READ_PAYLOAD;
        fsm->idx = 0;
        fsm->calc_crc = 0;
        return false;
    }
    switch (fsm->state) {
        case FSM_WAIT_START: return false;
        case FSM_READ_PAYLOAD:
            if (byte == '*') {
                fsm->buffer[fsm->idx] = '\0';
                fsm->state = FSM_READ_CS1;
            } else if (fsm->idx < 80) {
                fsm->buffer[fsm->idx++] = (char)byte;
                fsm->calc_crc ^= byte;
            } else {
                fsm->state = FSM_WAIT_START;
            }
            return false;
        case FSM_READ_CS1: {
            int v = hex_val((char)byte);
            if (v >= 0) { fsm->rx_crc = (uint8_t)(v << 4); fsm->state = FSM_READ_CS2; }
            else { fsm->state = FSM_WAIT_START; }
            return false;
        }
        case FSM_READ_CS2: {
            int v = hex_val((char)byte);
            if (v >= 0) {
                fsm->rx_crc |= (uint8_t)v;
                fsm->state = (fsm->rx_crc == fsm->calc_crc) ? FSM_WAIT_CR : FSM_WAIT_START;
            } else { fsm->state = FSM_WAIT_START; }
            return false;
        }
        case FSM_WAIT_CR:
            if (byte == '\r') fsm->state = FSM_WAIT_LF;
            else fsm->state = FSM_WAIT_START;
            return false;
        case FSM_WAIT_LF:
            fsm->state = FSM_WAIT_START;
            return (byte == '\n');
    }
    return false;
}
