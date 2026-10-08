#include "ring_buffer.h"

/**
 * @file ring_buffer.c
 * @brief Реалізація методів асинхронного потокобезпечного кільцевого буфера.
 */

void ring_buffer_init(ring_buffer_t *rb, uint8_t *storage, uint16_t capacity) {
    if (rb == NULL || storage == NULL || capacity == 0) {
        return;
    }
    rb->buffer = storage;
    rb->capacity = capacity;
    rb->head = 0;
    rb->tail = 0;
    rb->count = 0;
}

bool ring_buffer_is_empty(const ring_buffer_t *rb) {
    if (rb == NULL) {
        return true;
    }
    return (rb->count == 0);
}

bool ring_buffer_is_full(const ring_buffer_t *rb) {
    if (rb == NULL) {
        return false;
    }
    return (rb->count >= rb->capacity);
}

uint16_t ring_buffer_available(const ring_buffer_t *rb) {
    if (rb == NULL) {
        return 0;
    }
    return rb->count;
}

bool ring_buffer_push(ring_buffer_t *rb, uint8_t byte) {
    if (rb == NULL || rb->buffer == NULL) {
        return false;
    }
    if (rb->count >= rb->capacity) {
        /* Буфер переповнений - відкидаємо байт для захисту від перезапису */
        return false;
    }

    rb->buffer[rb->head] = byte;
    rb->head = (uint16_t)((rb->head + 1) % rb->capacity);
    rb->count++;
    return true;
}

bool ring_buffer_pop(ring_buffer_t *rb, uint8_t *byte) {
    if (rb == NULL || rb->buffer == NULL || byte == NULL) {
        return false;
    }
    if (rb->count == 0) {
        return false;
    }

    *byte = rb->buffer[rb->tail];
    rb->tail = (uint16_t)((rb->tail + 1) % rb->capacity);
    rb->count--;
    return true;
}

bool ring_buffer_peek(const ring_buffer_t *rb, uint8_t *byte) {
    if (rb == NULL || rb->buffer == NULL || byte == NULL) {
        return false;
    }
    if (rb->count == 0) {
        return false;
    }

    *byte = rb->buffer[rb->tail];
    return true;
}

void ring_buffer_clear(ring_buffer_t *rb) {
    if (rb == NULL) {
        return;
    }
    rb->head = 0;
    rb->tail = 0;
    rb->count = 0;
}
