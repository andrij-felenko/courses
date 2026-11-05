#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define RING_BUF_CAPACITY 256
#define RING_BUF_MASK     (RING_BUF_CAPACITY - 1)
#define FRAME_SOF         0xAA

typedef struct {
    uint8_t buffer[RING_BUF_CAPACITY];
    volatile size_t head;
    volatile size_t tail;
} ring_buffer_t;

typedef enum {
    PARSER_STATE_SOF,
    PARSER_STATE_LEN,
    PARSER_STATE_DATA,
    PARSER_STATE_CRC
} parser_state_t;

typedef struct {
    parser_state_t state;
    uint8_t len;
    uint8_t index;
    uint8_t payload[64];
    uint8_t crc;
} frame_parser_t;

typedef struct {
    ring_buffer_t rx_ring;
    frame_parser_t parser;
    uint32_t frames_received;
    uint32_t overrun_count;
} uart_pipeline_t;

void uart_pipeline_init(uart_pipeline_t *pipe) {
    pipe->rx_ring.head = 0;
    pipe->rx_ring.tail = 0;
    pipe->parser.state = PARSER_STATE_SOF;
    pipe->frames_received = 0;
    pipe->overrun_count = 0;
}

// Викликається з ISR при отриманні байта (RXNE)
void uart_pipeline_isr_push(uart_pipeline_t *pipe, uint8_t byte) {
    size_t next_head = (pipe->rx_ring.head + 1) & RING_BUF_MASK;
    if (next_head != pipe->rx_ring.tail) {
        pipe->rx_ring.buffer[pipe->rx_ring.head] = byte;
        pipe->rx_ring.head = next_head;
    } else {
        pipe->overrun_count++;
    }
}

// Вилучення байта з буфера у фоновому контексті
static bool ring_buffer_pop(ring_buffer_t *rb, uint8_t *byte) {
    if (rb->head == rb->tail) {
        return false;
    }
    *byte = rb->buffer[rb->tail];
    rb->tail = (rb->tail + 1) & RING_BUF_MASK;
    return true;
}

// Потоковий парсер вхідних даних
static void parse_byte(uart_pipeline_t *pipe, uint8_t byte) {
    frame_parser_t *p = &pipe->parser;
    switch (p->state) {
        case PARSER_STATE_SOF:
            if (byte == FRAME_SOF) {
                p->state = PARSER_STATE_LEN;
                p->crc = byte;
            }
            break;
        case PARSER_STATE_LEN:
            if (byte > 0 && byte <= sizeof(p->payload)) {
                p->len = byte;
                p->index = 0;
                p->crc ^= byte;
                p->state = PARSER_STATE_DATA;
            } else {
                p->state = PARSER_STATE_SOF;
            }
            break;
        case PARSER_STATE_DATA:
            p->payload[p->index++] = byte;
            p->crc ^= byte;
            if (p->index >= p->len) {
                p->state = PARSER_STATE_CRC;
            }
            break;
        case PARSER_STATE_CRC:
            if (byte == p->crc) {
                pipe->frames_received++;
            }
            p->state = PARSER_STATE_SOF;
            break;
    }
}

// Фонова обробка накопичених у буфері даних
void uart_pipeline_process(uart_pipeline_t *pipe) {
    uint8_t byte;
    while (ring_buffer_pop(&pipe->rx_ring, &byte)) {
        parse_byte(pipe, byte);
    }
}
