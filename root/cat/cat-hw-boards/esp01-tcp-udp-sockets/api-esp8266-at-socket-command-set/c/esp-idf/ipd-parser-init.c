#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    STATE_SEARCH_IPD,
    STATE_READ_LINK_ID,
    STATE_READ_LENGTH,
    STATE_READ_PAYLOAD
} ipd_parser_state_t;

typedef struct {
    ipd_parser_state_t state;
    uint8_t link_id;
    uint16_t payload_len;
    uint16_t bytes_read;
    uint8_t buffer[2048];
    uint8_t match_idx;
} ipd_parser_t;

void ipd_parser_init(ipd_parser_t *parser) {
    parser->state = STATE_SEARCH_IPD;
    parser->link_id = 0;
    parser->payload_len = 0;
    parser->bytes_read = 0;
    parser->match_idx = 0;
}

void ipd_parser_process_byte(ipd_parser_t *parser, uint8_t byte) {
    const char *header = "+IPD,";
    
    switch (parser->state) {
        case STATE_SEARCH_IPD:
            if (byte == (uint8_t)header[parser->match_idx]) {
                parser->match_idx++;
                if (parser->match_idx == 5) {
                    parser->state = STATE_READ_LINK_ID;
                    parser->link_id = 0;
                    parser->payload_len = 0;
                    parser->match_idx = 0;
                }
            } else {
                parser->match_idx = (byte == (uint8_t)header[0]) ? 1 : 0;
            }
            break;

        case STATE_READ_LINK_ID:
            if (byte >= '0' && byte <= '4') {
                parser->link_id = byte - '0';
            } else if (byte == ',') {
                parser->state = STATE_READ_LENGTH;
            }
            break;

        case STATE_READ_LENGTH:
            if (byte >= '0' && byte <= '9') {
                parser->payload_len = parser->payload_len * 10 + (byte - '0');
            } else if (byte == ':') {
                parser->bytes_read = 0;
                parser->state = (parser->payload_len > 0) ? STATE_READ_PAYLOAD : STATE_SEARCH_IPD;
            }
            break;

        case STATE_READ_PAYLOAD:
            if (parser->bytes_read < sizeof(parser->buffer)) {
                parser->buffer[parser->bytes_read] = byte;
            }
            parser->bytes_read++;
            if (parser->bytes_read >= parser->payload_len) {
                // Пакет повністю прийнято, обробка корисного навантаження
                parser->state = STATE_SEARCH_IPD;
            }
            break;
    }
}
