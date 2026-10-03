#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>

#define RING_BUF_SIZE 256
#define LINE_BUF_SIZE 128
#define IPD_BUF_SIZE  256

typedef struct {
    uint8_t data[RING_BUF_SIZE];
    uint16_t head;
    uint16_t tail;
} RingBuffer;

typedef enum {
    PARSER_STATE_LINE,
    PARSER_STATE_IPD_PAYLOAD
} ParserState;

typedef enum {
    EVENT_NONE,
    EVENT_OK,
    EVENT_ERROR,
    EVENT_SEND_OK,
    EVENT_IPD_DATA
} ParserEventType;

typedef struct {
    ParserEventType type;
    uint8_t link_id;
    uint16_t payload_len;
    uint8_t payload[IPD_BUF_SIZE];
} ParserEvent;

static RingBuffer rx_ring;

void ring_buffer_put(uint8_t byte) {
    uint16_t next_head = (rx_ring.head + 1) % RING_BUF_SIZE;
    if (next_head != rx_ring.tail) {
        rx_ring.data[rx_ring.head] = byte;
        rx_ring.head = next_head;
    }
}

bool ring_buffer_get(uint8_t *byte) {
    if (rx_ring.head == rx_ring.tail) {
        return false;
    }
    *byte = rx_ring.data[rx_ring.tail];
    rx_ring.tail = (rx_ring.tail + 1) % RING_BUF_SIZE;
    return true;
}

typedef struct {
    ParserState state;
    char line_buf[LINE_BUF_SIZE];
    uint16_t line_pos;
    uint8_t ipd_link_id;
    uint16_t ipd_expected_len;
    uint16_t ipd_received_len;
    uint8_t ipd_buf[IPD_BUF_SIZE];
} EspAtParser;

void esp_parser_init(EspAtParser *parser) {
    parser->state = PARSER_STATE_LINE;
    parser->line_pos = 0;
    parser->ipd_link_id = 0;
    parser->ipd_expected_len = 0;
    parser->ipd_received_len = 0;
}

bool esp_parser_process_byte(EspAtParser *parser, uint8_t byte, ParserEvent *out_event) {
    out_event->type = EVENT_NONE;

    if (parser->state == PARSER_STATE_IPD_PAYLOAD) {
        if (parser->ipd_received_len < IPD_BUF_SIZE) {
            parser->ipd_buf[parser->ipd_received_len] = byte;
        }
        parser->ipd_received_len++;

        if (parser->ipd_received_len >= parser->ipd_expected_len) {
            out_event->type = EVENT_IPD_DATA;
            out_event->link_id = parser->ipd_link_id;
            out_event->payload_len = (parser->ipd_received_len < IPD_BUF_SIZE) ? 
                                      parser->ipd_received_len : IPD_BUF_SIZE;
            memcpy(out_event->payload, parser->ipd_buf, out_event->payload_len);
            
            parser->state = PARSER_STATE_LINE;
            parser->line_pos = 0;
            return true;
        }
        return false;
    }

    if (byte == '\r') {
        return false;
    }

    if (byte == '\n') {
        parser->line_buf[parser->line_pos] = '\0';
        
        if (strcmp(parser->line_buf, "OK") == 0) {
            out_event->type = EVENT_OK;
        } else if (strcmp(parser->line_buf, "ERROR") == 0) {
            out_event->type = EVENT_ERROR;
        } else if (strcmp(parser->line_buf, "SEND OK") == 0) {
            out_event->type = EVENT_SEND_OK;
        }

        parser->line_pos = 0;
        return (out_event->type != EVENT_NONE);
    }

    if (parser->line_pos < (LINE_BUF_SIZE - 1)) {
        parser->line_buf[parser->line_pos++] = (char)byte;
        parser->line_buf[parser->line_pos] = '\0';
    } else {
        parser->line_pos = 0;
    }

    if (strncmp(parser->line_buf, "+IPD,", 5) == 0 && byte == ':') {
        int link_id = 0;
        int len = 0;
        if (sscanf(parser->line_buf, "+IPD,%d,%d:", &link_id, &len) == 2) {
            parser->ipd_link_id = (uint8_t)link_id;
            parser->ipd_expected_len = (uint16_t)len;
        } else if (sscanf(parser->line_buf, "+IPD,%d:", &len) == 1) {
            parser->ipd_link_id = 0;
            parser->ipd_expected_len = (uint16_t)len;
        }
        parser->ipd_received_len = 0;
        parser->state = PARSER_STATE_IPD_PAYLOAD;
        parser->line_pos = 0;
    }

    return false;
}
