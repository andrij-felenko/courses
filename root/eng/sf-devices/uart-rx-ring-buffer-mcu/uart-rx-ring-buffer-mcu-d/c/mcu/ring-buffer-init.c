#include <stdint.h>
#include <stdbool.h>

#define RING_BUFFER_SIZE 128U  /* Розмір мусить бути степенем двійки */
#define RING_BUFFER_MASK (RING_BUFFER_SIZE - 1U)

typedef struct {
    uint8_t buffer[RING_BUFFER_SIZE];
    volatile uint32_t head;
    volatile uint32_t tail;
} ring_buffer_t;

void ring_buffer_init(ring_buffer_t *rb) {
    rb->head = 0;
    rb->tail = 0;
}

bool ring_buffer_push(ring_buffer_t *rb, uint8_t data) {
    uint32_t next_head = (rb->head + 1U) & RING_BUFFER_MASK;
    if (next_head == rb->tail) {
        return false; /* Буфер повний: переповнення */
    }
    rb->buffer[rb->head] = data;
    rb->head = next_head; /* Атомарне оновлення вказівника для 32-бітних MCU */
    return true;
}

bool ring_buffer_pop(ring_buffer_t *rb, uint8_t *data) {
    if (rb->head == rb->tail) {
        return false; /* Буфер порожній */
    }
    *data = rb->buffer[rb->tail];
    rb->tail = (rb->tail + 1U) & RING_BUFFER_MASK;
    return true;
}

uint32_t ring_buffer_available(const ring_buffer_t *rb) {
    return (rb->head - rb->tail) & RING_BUFFER_MASK;
}
