#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

typedef struct {
    uint8_t *buffer;
    size_t capacity;
    size_t mask;
    volatile size_t head;
    volatile size_t tail;
} ring_buffer_t;

typedef enum {
    RING_BUFFER_OK = 0,
    RING_BUFFER_ERR_EMPTY,
    RING_BUFFER_ERR_FULL,
    RING_BUFFER_ERR_INVALID_PARAM
} ring_buffer_status_t;

bool ring_buffer_init(ring_buffer_t *rb, uint8_t *storage, size_t capacity) {
    if (!rb || !storage || capacity == 0 || (capacity & (capacity - 1)) != 0) {
        return false;
    }
    rb->buffer = storage;
    rb->capacity = capacity;
    rb->mask = capacity - 1;
    rb->head = 0;
    rb->tail = 0;
    return true;
}

ring_buffer_status_t ring_buffer_push_from_isr(ring_buffer_t *rb, uint8_t data) {
    size_t next_head = (rb->head + 1) & rb->mask;
    if (next_head == rb->tail) {
        return RING_BUFFER_ERR_FULL;
    }
    rb->buffer[rb->head] = data;
    rb->head = next_head;
    return RING_BUFFER_OK;
}

ring_buffer_status_t ring_buffer_pop(ring_buffer_t *rb, uint8_t *data) {
    if (rb->head == rb->tail) {
        return RING_BUFFER_ERR_EMPTY;
    }
    *data = rb->buffer[rb->tail];
    rb->tail = (rb->tail + 1) & rb->mask;
    return RING_BUFFER_OK;
}

size_t ring_buffer_available(const ring_buffer_t *rb) {
    return (rb->head - rb->tail) & rb->mask;
}
