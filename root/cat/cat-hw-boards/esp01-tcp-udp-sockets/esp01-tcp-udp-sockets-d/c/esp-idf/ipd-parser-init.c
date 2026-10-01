#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

typedef enum {
    IPD_STATE_IDLE,
    IPD_STATE_PREFIX,
    IPD_STATE_LINK_ID,
    IPD_STATE_LENGTH,
    IPD_STATE_BODY
} ipd_parser_state_t;

typedef struct {
    ipd_parser_state_t state;
    uint8_t prefix_idx;
    uint8_t link_id;
    uint16_t packet_len;
    uint16_t bytes_read;
    bool is_multiconn;
    uint8_t rx_buffer[1024];
} ipd_parser_t;

static const char IPD_PREFIX[] = "+IPD,";

void ipd_parser_init(ipd_parser_t *parser, bool is_multiconn) {
    parser->state = IPD_STATE_IDLE;
    parser->prefix_idx = 0;
    parser->link_id = 0;
    parser->packet_len = 0;
    parser->bytes_read = 0;
    parser->is_multiconn = is_multiconn;
}

void ipd_on_payload_byte(uint8_t link_id, uint8_t byte) {
    // Обробка бінарного байта корисного навантаження
}

void ipd_parser_process_byte(ipd_parser_t *parser, uint8_t byte) {
    switch (parser->state) {
    case IPD_STATE_IDLE:
        if (byte == '+') {
            parser->prefix_idx = 1;
            parser->state = IPD_STATE_PREFIX;
        }
        break;

    case IPD_STATE_PREFIX:
        if (byte == IPD_PREFIX[parser->prefix_idx]) {
            parser->prefix_idx++;
            if (parser->prefix_idx >= 5) {
                if (parser->is_multiconn) {
                    parser->link_id = 0;
                    parser->state = IPD_STATE_LINK_ID;
                } else {
                    parser->link_id = 0;
                    parser->packet_len = 0;
                    parser->state = IPD_STATE_LENGTH;
                }
            }
        } else {
            parser->state = IPD_STATE_IDLE;
        }
        break;

    case IPD_STATE_LINK_ID:
        if (byte >= '0' && byte <= '4') {
            parser->link_id = byte - '0';
        } else if (byte == ',') {
            parser->packet_len = 0;
            parser->state = IPD_STATE_LENGTH;
        } else {
            parser->state = IPD_STATE_IDLE;
        }
        break;

    case IPD_STATE_LENGTH:
        if (byte >= '0' && byte <= '9') {
            parser->packet_len = parser->packet_len * 10 + (byte - '0');
        } else if (byte == ':') {
            parser->bytes_read = 0;
            if (parser->packet_len > 0) {
                parser->state = IPD_STATE_BODY;
            } else {
                parser->state = IPD_STATE_IDLE;
            }
        } else {
            parser->state = IPD_STATE_IDLE;
        }
        break;

    case IPD_STATE_BODY:
        ipd_on_payload_byte(parser->link_id, byte);
        parser->bytes_read++;
        if (parser->bytes_read >= parser->packet_len) {
            parser->state = IPD_STATE_IDLE;
        }
        break;
    }
}
