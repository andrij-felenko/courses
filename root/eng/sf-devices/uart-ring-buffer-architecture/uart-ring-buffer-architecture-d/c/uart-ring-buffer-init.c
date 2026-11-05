#include <stdint.h>
#include <stdbool.h>

// Розмір буфера обов'язково має бути степенем двійки (2^N)
#define UART_RING_BUFFER_SIZE 64U
#define UART_RING_BUFFER_MASK (UART_RING_BUFFER_SIZE - 1U)

typedef struct {
    uint8_t buffer[UART_RING_BUFFER_SIZE];
    volatile uint32_t head; // Модифікується тільки виробником (ISR / DMA)
    volatile uint32_t tail; // Модифікується тільки споживачем (Main Loop)
} uart_ring_buffer_t;

void uart_ring_buffer_init(uart_ring_buffer_t *rb) {
    rb->head = 0U;
    rb->tail = 0U;
}

bool uart_ring_buffer_is_empty(const uart_ring_buffer_t *rb) {
    return (rb->head == rb->tail);
}

bool uart_ring_buffer_is_full(const uart_ring_buffer_t *rb) {
    return (((rb->head + 1U) & UART_RING_BUFFER_MASK) == rb->tail);
}

bool uart_ring_buffer_put(uart_ring_buffer_t *rb, uint8_t data) {
    uint32_t next_head = (rb->head + 1U) & UART_RING_BUFFER_MASK;
    if (next_head == rb->tail) {
        return false; // Спроба запису в повний буфер (переповнення)
    }
    rb->buffer[rb->head] = data;
    rb->head = next_head; // Атомарне оновлення вказівника запису
    return true;
}

bool uart_ring_buffer_get(uart_ring_buffer_t *rb, uint8_t *data) {
    if (rb->head == rb->tail) {
        return false; // Буфер порожній
    }
    *data = rb->buffer[rb->tail];
    rb->tail = (rb->tail + 1U) & UART_RING_BUFFER_MASK; // Атомарне оновлення вказівника зчитаного
    return true;
}

uint32_t uart_ring_buffer_count(const uart_ring_buffer_t *rb) {
    return (rb->head - rb->tail) & UART_RING_BUFFER_MASK;
}
