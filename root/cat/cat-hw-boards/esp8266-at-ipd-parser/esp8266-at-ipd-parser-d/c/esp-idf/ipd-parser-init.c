#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

typedef enum {
    IPD_STATE_IDLE,
    IPD_STATE_PREFIX,
    IPD_STATE_LINK_ID,
    IPD_STATE_LEN,
    IPD_STATE_PAYLOAD
} ipd_parser_state_t;

typedef struct {
    ipd_parser_state_t state;
    uint8_t link_id;
    uint16_t len;
    uint16_t bytes_read;
    bool is_multilink;
} ipd_parser_t;

void ipd_parser_init(ipd_parser_t *parser, bool multilink) {
    parser->state = IPD_STATE_IDLE;
    parser->link_id = 0;
    parser->len = 0;
    parser->bytes_read = 0;
    parser->is_multilink = multilink;
}

void ipd_parse_char(ipd_parser_t *parser, char c) {
    switch (parser->state) {
        case IPD_STATE_IDLE:
            if (c == '+') parser->state = IPD_STATE_PREFIX;
            break;
        case IPD_STATE_PREFIX:
            // Спрощений приклад переходу після префікса "+IPD,"
            if (c == ',') {
                parser->state = parser->is_multilink ? IPD_STATE_LINK_ID : IPD_STATE_LEN;
                parser->len = 0;
                parser->link_id = 0;
            }
            break;
        case IPD_STATE_LINK_ID:
            if (c >= '0' && c <= '9') {
                parser->link_id = c - '0';
            } else if (c == ',') {
                parser->state = IPD_STATE_LEN;
                parser->len = 0;
            }
            break;
        case IPD_STATE_LEN:
            if (c >= '0' && c <= '9') {
                parser->len = (uint16_t)(parser->len * 10 + (c - '0'));
            } else if (c == ':') {
                parser->state = IPD_STATE_PAYLOAD;
                parser->bytes_read = 0;
            }
            break;
        case IPD_STATE_PAYLOAD:
            // Прямий побайтовий прийом бінарного навантаження
            parser->bytes_read++;
            if (parser->bytes_read >= parser->len) {
                parser->state = IPD_STATE_IDLE;
            }
            break;
    }
}
