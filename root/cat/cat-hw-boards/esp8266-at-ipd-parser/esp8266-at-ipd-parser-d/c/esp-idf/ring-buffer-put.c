#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define RING_BUFFER_SIZE 1024
#define IPD_MAX_PAYLOAD 1460
#define TIMEOUT_MS 100

typedef struct {
    uint8_t buffer[RING_BUFFER_SIZE];
    uint16_t head;
    uint16_t tail;
} ring_buffer_t;

typedef enum {
    FSM_IDLE,
    FSM_PREFIX,
    FSM_LINK_ID,
    FSM_LEN,
    FSM_PAYLOAD
} fsm_state_t;

typedef struct {
    fsm_state_t state;
    uint8_t prefix_idx;
    uint8_t link_id;
    uint16_t payload_len;
    uint16_t bytes_received;
    uint32_t last_byte_time_ms;
    bool is_multilink;
    uint8_t payload[IPD_MAX_PAYLOAD];
} safe_ipd_parser_t;

void ring_buffer_put(ring_buffer_t *rb, uint8_t byte) {
    uint16_t next = (rb->head + 1) % RING_BUFFER_SIZE;
    if (next != rb->tail) {
        rb->buffer[rb->head] = byte;
        rb->head = next;
    }
}

bool ring_buffer_get(ring_buffer_t *rb, uint8_t *byte) {
    if (rb->head == rb->tail) return false;
    *byte = rb->buffer[rb->tail];
    rb->tail = (rb->tail + 1) % RING_BUFFER_SIZE;
    return true;
}

void safe_parser_init(safe_ipd_parser_t *p, bool multilink) {
    p->state = FSM_IDLE;
    p->prefix_idx = 0;
    p->link_id = 0;
    p->payload_len = 0;
    p->bytes_received = 0;
    p->last_byte_time_ms = 0;
    p->is_multilink = multilink;
}

void safe_parser_check_timeout(safe_ipd_parser_t *p, uint32_t current_time_ms) {
    if (p->state != FSM_IDLE && (current_time_ms - p->last_byte_time_ms > TIMEOUT_MS)) {
        // Скидання автомата за часовим таймаутом переривання зв'язку
        p->state = FSM_IDLE;
        p->prefix_idx = 0;
        p->bytes_received = 0;
    }
}

void safe_parser_process_byte(safe_ipd_parser_t *p, uint8_t byte, uint32_t current_time_ms) {
    p->last_byte_time_ms = current_time_ms;
    char c = (char)byte;

    switch (p->state) {
        case FSM_IDLE:
            if (c == '+') {
                p->state = FSM_PREFIX;
                p->prefix_idx = 0;
            }
            break;
        case FSM_PREFIX:
            if ("IPD,"[p->prefix_idx] == c) {
                p->prefix_idx++;
                if (p->prefix_idx == 4) {
                    p->state = p->is_multilink ? FSM_LINK_ID : FSM_LEN;
                    p->payload_len = 0;
                    p->link_id = 0;
                }
            } else {
                p->state = FSM_IDLE;
            }
            break;
        case FSM_LINK_ID:
            if (c >= '0' && c <= '9') {
                p->link_id = p->link_id * 10 + (c - '0');
            } else if (c == ',') {
                p->state = FSM_LEN;
            } else {
                p->state = FSM_IDLE;
            }
            break;
        case FSM_LEN:
            if (c >= '0' && c <= '9') {
                p->payload_len = p->payload_len * 10 + (c - '0');
            } else if (c == ':') {
                p->bytes_received = 0;
                p->state = (p->payload_len > 0) ? FSM_PAYLOAD : FSM_IDLE;
            } else {
                p->state = FSM_IDLE;
            }
            break;
        case FSM_PAYLOAD:
            if (p->bytes_received < IPD_MAX_PAYLOAD) {
                p->payload[p->bytes_received++] = byte;
            }
            if (p->bytes_received >= p->payload_len) {
                // Пакет успішно прийнято
                p->state = FSM_IDLE;
            }
            break;
    }
}
