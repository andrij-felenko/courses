#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define PROTOCOL_HEADER_BYTE    0xAA
#define PROTOCOL_MAX_PAYLOAD    64

typedef enum {
    PARSER_STATE_HEADER = 0,
    PARSER_STATE_LENGTH,
    PARSER_STATE_PAYLOAD,
    PARSER_STATE_CHECKSUM
} parser_state_t;

typedef struct {
    parser_state_t state;
    uint8_t payload_len;
    uint8_t bytes_read;
    uint8_t checksum;
    uint8_t payload[PROTOCOL_MAX_PAYLOAD];
} frame_parser_t;

void frame_parser_init(frame_parser_t *parser) {
    if (!parser) return;
    parser->state = PARSER_STATE_HEADER;
    parser->payload_len = 0;
    parser->bytes_read = 0;
    parser->checksum = 0;
}

bool frame_parser_feed_byte(frame_parser_t *parser, uint8_t byte, uint8_t *out_frame, size_t *out_len) {
    if (!parser) return false;

    switch (parser->state) {
    case PARSER_STATE_HEADER:
        if (byte == PROTOCOL_HEADER_BYTE) {
            parser->checksum = byte;
            parser->state = PARSER_STATE_LENGTH;
        }
        break;

    case PARSER_STATE_LENGTH:
        if (byte == 0 || byte > PROTOCOL_MAX_PAYLOAD) {
            parser->state = PARSER_STATE_HEADER;
        } else {
            parser->payload_len = byte;
            parser->bytes_read = 0;
            parser->checksum ^= byte;
            parser->state = PARSER_STATE_PAYLOAD;
        }
        break;

    case PARSER_STATE_PAYLOAD:
        parser->payload[parser->bytes_read++] = byte;
        parser->checksum ^= byte;
        if (parser->bytes_read >= parser->payload_len) {
            parser->state = PARSER_STATE_CHECKSUM;
        }
        break;

    case PARSER_STATE_CHECKSUM:
        parser->state = PARSER_STATE_HEADER;
        if (byte == parser->checksum && out_frame && out_len) {
            for (size_t i = 0; i < parser->payload_len; ++i) {
                out_frame[i] = parser->payload[i];
            }
            *out_len = parser->payload_len;
            return true;
        }
        break;
    }
    return false;
}
