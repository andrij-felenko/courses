#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define RING_BUFFER_SIZE 128U /* Має бути степенем двійки 2^7 */
#define RING_BUFFER_MASK (RING_BUFFER_SIZE - 1U)

typedef struct {
    uint8_t buffer[RING_BUFFER_SIZE];
    volatile size_t head;
    volatile size_t tail;
} ring_buffer_t;

void ring_buffer_init(ring_buffer_t *ring) {
    ring->head = 0;
    ring->tail = 0;
}

bool ring_buffer_push(ring_buffer_t *ring, uint8_t data) {
    size_t next_head = (ring->head + 1U) & RING_BUFFER_MASK;
    if (next_head == ring->tail) {
        return false; /* Буфер переповнений */
    }
    ring->buffer[ring->head] = data;
    /* Бар'єр пам'яті гарантує запис даних перед оновленням head */
    __asm__ volatile("" ::: "memory");
    ring->head = next_head;
    return true;
}

bool ring_buffer_pop(ring_buffer_t *ring, uint8_t *data) {
    if (ring->head == ring->tail) {
        return false; /* Буфер порожній */
    }
    *data = ring->buffer[ring->tail];
    __asm__ volatile("" ::: "memory");
    ring->tail = (ring->tail + 1U) & RING_BUFFER_MASK;
    return true;
}

size_t ring_buffer_count(const ring_buffer_t *ring) {
    return (ring->head - ring->tail) & RING_BUFFER_MASK;
}
