#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

/* ═════════════════════════════════════════════════════════════════════════════
 * 1. БРОКЕР SERVER-SENT EVENTS (SSE) З КІЛЬЦЕВИМ БУФЕРОМ НА C
 * ═════════════════════════════════════════════════════════════════════════════ */

#define MAX_EVENT_DATA 1024
#define MAX_EVENT_NAME 64

typedef struct {
    uint64_t id;
    char event_type[MAX_EVENT_NAME];
    char data[MAX_EVENT_DATA];
} sse_event_t;

typedef struct {
    sse_event_t *events;
    size_t capacity;
    size_t head;
    size_t count;
    uint64_t next_id;
} sse_ring_buffer_t;

sse_ring_buffer_t* sse_buffer_create(size_t capacity) {
    sse_ring_buffer_t *rb = (sse_ring_buffer_t*)malloc(sizeof(sse_ring_buffer_t));
    if (!rb) return NULL;
    rb->events = (sse_event_t*)calloc(capacity, sizeof(sse_event_t));
    if (!rb->events) {
        free(rb);
        return NULL;
    }
    rb->capacity = capacity;
    rb->head = 0;
    rb->count = 0;
    rb->next_id = 1;
    return rb;
}

void sse_buffer_free(sse_ring_buffer_t *rb) {
    if (rb) {
        free(rb->events);
        free(rb);
    }
}

uint64_t sse_buffer_push(sse_ring_buffer_t *rb, const char *event_type, const char *data) {
    uint64_t current_id = rb->next_id++;
    size_t index = (rb->head + rb->count) % rb->capacity;

    rb->events[index].id = current_id;
    strncpy(rb->events[index].event_type, event_type ? event_type : "", MAX_EVENT_NAME - 1);
    rb->events[index].event_type[MAX_EVENT_NAME - 1] = '\0';
    strncpy(rb->events[index].data, data ? data : "", MAX_EVENT_DATA - 1);
    rb->events[index].data[MAX_EVENT_DATA - 1] = '\0';

    if (rb->count < rb->capacity) {
        rb->count++;
    } else {
        rb->head = (rb->head + 1) % rb->capacity; /* витіснення найстарішої */
    }
    return current_id;
}

/* Форматування події у вихідний рядок */
int sse_format_event(const sse_event_t *ev, char *dest, size_t max_len) {
    if (ev->event_type[0] != '\0') {
        return snprintf(dest, max_len, "id: %llu\nevent: %s\ndata: %s\n\n",
                        (unsigned long long)ev->id, ev->event_type, ev->data);
    }
    return snprintf(dest, max_len, "id: %llu\ndata: %s\n\n",
                    (unsigned long long)ev->id, ev->data);
}

/* ═════════════════════════════════════════════════════════════════════════════
 * 2. ДЕКОДЕР КАДРІВ WEBSOCKET (RFC 6455) НА C
 * ═════════════════════════════════════════════════════════════════════════════ */

typedef enum {
    WS_OP_CONTINUATION = 0x0,
    WS_OP_TEXT         = 0x1,
    WS_OP_BINARY       = 0x2,
    WS_OP_CLOSE        = 0x8,
    WS_OP_PING         = 0x9,
    WS_OP_PONG         = 0xA
} ws_opcode_t;

typedef enum {
    WS_PARSE_OK = 0,
    WS_PARSE_NEED_MORE_DATA = 1,
    WS_PARSE_PROTOCOL_ERROR = 2
} ws_parse_status_t;

typedef struct {
    bool fin;
    ws_opcode_t opcode;
    bool masked;
    uint8_t *payload;
    size_t payload_len;
} ws_frame_t;

ws_parse_status_t ws_parse_frame(
    const uint8_t *buf, size_t buf_len,
    ws_frame_t *out_frame, size_t *bytes_consumed
) {
    *bytes_consumed = 0;
    if (buf_len < 2) return WS_PARSE_NEED_MORE_DATA;

    uint8_t byte0 = buf[0];
    uint8_t byte1 = buf[1];

    bool fin = (byte0 & 0x80) != 0;
    uint8_t rsv = (byte0 & 0x70) >> 4;
    if (rsv != 0) return WS_PARSE_PROTOCOL_ERROR;

    ws_opcode_t opcode = (ws_opcode_t)(byte0 & 0x0F);
    bool masked = (byte1 & 0x80) != 0;
    uint64_t payload_len = byte1 & 0x7F;
    size_t header_len = 2;

    if (payload_len == 126) {
        if (buf_len < header_len + 2) return WS_PARSE_NEED_MORE_DATA;
        payload_len = ((uint64_t)buf[2] << 8) | buf[3];
        header_len += 2;
    } else if (payload_len == 127) {
        if (buf_len < header_len + 8) return WS_PARSE_NEED_MORE_DATA;
        payload_len = 0;
        for (size_t i = 0; i < 8; ++i) {
            payload_len = (payload_len << 8) | buf[header_len + i];
        }
        header_len += 8;
    }

    uint8_t mask_key[4] = {0};
    if (masked) {
        if (buf_len < header_len + 4) return WS_PARSE_NEED_MORE_DATA;
        memcpy(mask_key, buf + header_len, 4);
        header_len += 4;
    }

    if (buf_len < header_len + payload_len) {
        return WS_PARSE_NEED_MORE_DATA;
    }

    out_frame->fin = fin;
    out_frame->opcode = opcode;
    out_frame->masked = masked;
    out_frame->payload_len = (size_t)payload_len;
    out_frame->payload = (uint8_t*)malloc(out_frame->payload_len + 1);
    if (!out_frame->payload) return WS_PARSE_PROTOCOL_ERROR;

    const uint8_t *src = buf + header_len;
    for (size_t i = 0; i < out_frame->payload_len; ++i) {
        out_frame->payload[i] = masked ? (src[i] ^ mask_key[i % 4]) : src[i];
    }
    out_frame->payload[out_frame->payload_len] = '\0'; /* зручність для тексту */

    *bytes_consumed = header_len + (size_t)payload_len;
    return WS_PARSE_OK;
}
