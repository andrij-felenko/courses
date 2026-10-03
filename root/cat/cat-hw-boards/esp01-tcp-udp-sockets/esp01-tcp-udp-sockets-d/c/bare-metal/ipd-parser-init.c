#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define IPD_MAX_PAYLOAD 512

typedef enum {
    IPD_STATE_IDLE,
    IPD_STATE_MATCH_PREFIX,
    IPD_STATE_READ_LINK_ID,
    IPD_STATE_READ_LENGTH,
    IPD_STATE_READ_PAYLOAD
} ipd_state_t;

typedef struct {
    ipd_state_t state;
    uint8_t link_id;
    uint16_t payload_len;
    uint16_t bytes_read;
    uint8_t prefix_idx;
    uint8_t payload[IPD_MAX_PAYLOAD];
} ipd_parser_t;

static const char IPD_PREFIX[] = "+IPD,";

void ipd_parser_init(ipd_parser_t *parser) {
    parser->state = IPD_STATE_IDLE;
    parser->link_id = 0;
    parser->payload_len = 0;
    parser->bytes_read = 0;
    parser->prefix_idx = 0;
}

bool ipd_parser_feed_byte(ipd_parser_t *parser, uint8_t byte, bool is_mux) {
    switch (parser->state) {
    case IPD_STATE_IDLE:
        if (byte == '+') {
            parser->prefix_idx = 1;
            parser->state = IPD_STATE_MATCH_PREFIX;
        }
        break;

    case IPD_STATE_MATCH_PREFIX:
        if (byte == IPD_PREFIX[parser->prefix_idx]) {
            parser->prefix_idx++;
            if (parser->prefix_idx == 5) {
                if (is_mux) {
                    parser->link_id = 0;
                    parser->state = IPD_STATE_READ_LINK_ID;
                } else {
                    parser->payload_len = 0;
                    parser->state = IPD_STATE_READ_LENGTH;
                }
            }
        } else {
            parser->state = IPD_STATE_IDLE;
        }
        break;

    case IPD_STATE_READ_LINK_ID:
        if (byte >= '0' && byte <= '9') {
            parser->link_id = byte - '0';
        } else if (byte == ',') {
            parser->payload_len = 0;
            parser->state = IPD_STATE_READ_LENGTH;
        } else {
            parser->state = IPD_STATE_IDLE;
        }
        break;

    case IPD_STATE_READ_LENGTH:
        if (byte >= '0' && byte <= '9') {
            parser->payload_len = (parser->payload_len * 10) + (byte - '0');
        } else if (byte == ':') {
            parser->bytes_read = 0;
            if (parser->payload_len > 0 && parser->payload_len <= IPD_MAX_PAYLOAD) {
                parser->state = IPD_STATE_READ_PAYLOAD;
            } else {
                parser->state = IPD_STATE_IDLE;
            }
        } else {
            parser->state = IPD_STATE_IDLE;
        }
        break;

    case IPD_STATE_READ_PAYLOAD:
        parser->payload[parser->bytes_read++] = byte;
        if (parser->bytes_read == parser->payload_len) {
            parser->state = IPD_STATE_IDLE;
            return true; // Кадр успішно зібрано
        }
        break;
    }
    return false;
}
