/* Приклад FSM-парсера заголовка +IPD на мові C */
#include <stdio.h>
#include <stdbool.h>

typedef enum {
    STATE_IDLE,
    STATE_PREFIX_PLUS,
    STATE_PREFIX_I,
    STATE_PREFIX_P,
    STATE_PREFIX_D,
    STATE_READ_ID,
    STATE_READ_LEN,
    STATE_READ_PAYLOAD
} ipd_parser_state_t;

typedef struct {
    ipd_parser_state_t state;
    int socket_id;
    int payload_len;
    int bytes_read;
} ipd_parser_t;

void ipd_parser_init(ipd_parser_t *parser) {
    parser->state = STATE_IDLE;
    parser->socket_id = 0;
    parser->payload_len = 0;
    parser->bytes_read = 0;
}

void ipd_parser_feed_char(ipd_parser_t *parser, char ch) {
    switch (parser->state) {
        case STATE_IDLE:
            if (ch == '+') parser->state = STATE_PREFIX_PLUS;
            break;
        case STATE_PREFIX_PLUS:
            parser->state = (ch == 'I') ? STATE_PREFIX_I : STATE_IDLE;
            break;
        case STATE_PREFIX_I:
            parser->state = (ch == 'P') ? STATE_PREFIX_P : STATE_IDLE;
            break;
        case STATE_PREFIX_P:
            parser->state = (ch == 'D') ? STATE_PREFIX_D : STATE_IDLE;
            break;
        case STATE_PREFIX_D:
            if (ch == ',') {
                parser->socket_id = 0;
                parser->state = STATE_READ_ID;
            } else {
                parser->state = STATE_IDLE;
            }
            break;
        case STATE_READ_ID:
            if (ch >= '0' && ch <= '9') {
                parser->socket_id = ch - '0';
            } else if (ch == ',') {
                parser->payload_len = 0;
                parser->state = STATE_READ_LEN;
            } else {
                parser->state = STATE_IDLE;
            }
            break;
        case STATE_READ_LEN:
            if (ch >= '0' && ch <= '9') {
                parser->payload_len = parser->payload_len * 10 + (ch - '0');
            } else if (ch == ':') {
                parser->bytes_read = 0;
                parser->state = STATE_READ_PAYLOAD;
            } else {
                parser->state = STATE_IDLE;
            }
            break;
        case STATE_READ_PAYLOAD:
            parser->bytes_read++;
            if (parser->bytes_read >= parser->payload_len) {
                parser->state = STATE_IDLE;
            }
            break;
    }
}
