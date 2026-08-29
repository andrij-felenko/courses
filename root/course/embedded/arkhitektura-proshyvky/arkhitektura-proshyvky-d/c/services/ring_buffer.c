/* services/ring_buffer.c — реалізація кільцевого буфера. */
#include "services/ring_buffer.h"

#include <string.h>

static unsigned char *slot_at(const ring_buffer_t *rb, size_t index)
{
    return rb->storage + index * rb->elem_size;
}

static size_t next_index(const ring_buffer_t *rb, size_t index)
{
    /* Ділення тут немає навмисно: на Cortex-M0 його немає в залізі,
     * а лічильник індексів усе одно рухається на одиницю. */
    const size_t n = index + 1u;
    return (n == rb->capacity) ? 0u : n;
}

bool ring_buffer_init(ring_buffer_t *rb, void *storage,
                      size_t elem_size, size_t capacity)
{
    if (rb == 0 || storage == 0 || elem_size == 0u || capacity == 0u) {
        return false;
    }
    rb->storage   = (unsigned char *)storage;
    rb->elem_size = elem_size;
    rb->capacity  = capacity;
    rb->head      = 0u;
    rb->tail      = 0u;
    rb->count     = 0u;
    return true;
}

void ring_buffer_reset(ring_buffer_t *rb)
{
    if (rb != 0) {
        rb->head  = 0u;
        rb->tail  = 0u;
        rb->count = 0u;
    }
}

size_t ring_buffer_count(const ring_buffer_t *rb)
{
    return (rb != 0) ? rb->count : 0u;
}

size_t ring_buffer_free(const ring_buffer_t *rb)
{
    return (rb != 0) ? (rb->capacity - rb->count) : 0u;
}

bool ring_buffer_is_empty(const ring_buffer_t *rb)
{
    return ring_buffer_count(rb) == 0u;
}

bool ring_buffer_is_full(const ring_buffer_t *rb)
{
    return rb != 0 && rb->count == rb->capacity;
}

bool ring_buffer_push(ring_buffer_t *rb, const void *elem)
{
    if (rb == 0 || rb->storage == 0 || elem == 0 || ring_buffer_is_full(rb)) {
        return false;
    }
    memcpy(slot_at(rb, rb->head), elem, rb->elem_size);
    rb->head = next_index(rb, rb->head);
    rb->count++;
    return true;
}

bool ring_buffer_push_overwrite(ring_buffer_t *rb, const void *elem)
{
    if (rb == 0 || rb->storage == 0 || elem == 0) {
        return false;
    }

    bool dropped = false;
    if (ring_buffer_is_full(rb)) {
        rb->tail = next_index(rb, rb->tail);
        rb->count--;
        dropped = true;
    }
    memcpy(slot_at(rb, rb->head), elem, rb->elem_size);
    rb->head = next_index(rb, rb->head);
    rb->count++;
    return dropped;
}

bool ring_buffer_pop(ring_buffer_t *rb, void *out_elem)
{
    if (rb == 0 || rb->storage == 0 || out_elem == 0 || rb->count == 0u) {
        return false;
    }
    memcpy(out_elem, slot_at(rb, rb->tail), rb->elem_size);
    rb->tail = next_index(rb, rb->tail);
    rb->count--;
    return true;
}

bool ring_buffer_peek(const ring_buffer_t *rb, void *out_elem)
{
    if (rb == 0 || rb->storage == 0 || out_elem == 0 || rb->count == 0u) {
        return false;
    }
    memcpy(out_elem, slot_at(rb, rb->tail), rb->elem_size);
    return true;
}
