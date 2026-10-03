#include <stdint.h>
#include <stdbool.h>
#include <ctype.h>

typedef enum {
    IPD_SEARCH_PREFIX,
    IPD_PARSE_LINK_ID,
    IPD_PARSE_LEN,
    IPD_STREAM_PAYLOAD
} ipd_parser_state_t;

typedef struct {
    ipd_parser_state_t state;
    uint8_t match_idx;
    uint8_t link_id;
    uint16_t bytes_remaining;
} ipd_parser_t;

static const char IPD_PREFIX[] = "+IPD,";

void ipd_parser_init(ipd_parser_t *parser) {
    parser->state = IPD_SEARCH_PREFIX;
    parser->match_idx = 0;
    parser->link_id = 0;
    parser->bytes_remaining = 0;
}

bool ipd_parser_process_byte(ipd_parser_t *parser, uint8_t byte, void (*on_payload_byte)(uint8_t link_id, uint8_t b)) {
    switch (parser->state) {
        case IPD_SEARCH_PREFIX:
            if (byte == (uint8_t)IPD_PREFIX[parser->match_idx]) {
                parser->match_idx++;
                if (IPD_PREFIX[parser->match_idx] == '\0') {
                    parser->state = IPD_PARSE_LINK_ID;
                    parser->link_id = 0;
                    parser->match_idx = 0;
                }
            } else {
                parser->match_idx = (byte == (uint8_t)IPD_PREFIX[0]) ? 1 : 0;
            }
            break;

        case IPD_PARSE_LINK_ID:
            if (isdigit(byte)) {
                parser->link_id = parser->link_id * 10 + (byte - '0');
            } else if (byte == ',') {
                parser->state = IPD_PARSE_LEN;
                parser->bytes_remaining = 0;
            } else {
                parser->state = IPD_SEARCH_PREFIX;
            }
            break;

        case IPD_PARSE_LEN:
            if (isdigit(byte)) {
                parser->bytes_remaining = parser->bytes_remaining * 10 + (byte - '0');
            } else if (byte == ':') {
                if (parser->bytes_remaining > 0) {
                    parser->state = IPD_STREAM_PAYLOAD;
                } else {
                    parser->state = IPD_SEARCH_PREFIX;
                }
            } else {
                parser->state = IPD_SEARCH_PREFIX;
            }
            break;

        case IPD_STREAM_PAYLOAD:
            if (on_payload_byte) {
                on_payload_byte(parser->link_id, byte);
            }
            parser->bytes_remaining--;
            if (parser->bytes_remaining == 0) {
                parser->state = IPD_SEARCH_PREFIX;
            }
            return true;
    }
    return false;
}
