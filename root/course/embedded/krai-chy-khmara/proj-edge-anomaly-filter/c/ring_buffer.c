#include "ring_buffer.h"

#include <stddef.h>

void ring_buffer_clear(ring_buffer_t *rb)
{
    rb->head  = 0;
    rb->count = 0;
    /* Самі дані не чистимо: за межами count їх ніхто не читає,
       а memset на 128 байт у задачі на 100 Гц — марна робота. */
}

void ring_buffer_push(ring_buffer_t *rb, float sample)
{
    rb->data[rb->head] = sample;
    rb->head = (rb->head + 1u) % RING_BUFFER_CAPACITY;
    if (rb->count < RING_BUFFER_CAPACITY) {
        rb->count++;
    }
}

uint32_t ring_buffer_copy(const ring_buffer_t *rb, float *dest, uint32_t dest_len)
{
    if (dest == NULL || dest_len == 0u) {
        return 0u;
    }

    const uint32_t to_copy = (rb->count < dest_len) ? rb->count : dest_len;

    /* Найстаріша вибірка лежить на count позицій позаду голови.
       Додаємо CAPACITY, щоб різниця не пішла в мінус на беззнаковому. */
    uint32_t idx = (rb->head + RING_BUFFER_CAPACITY - rb->count) % RING_BUFFER_CAPACITY;

    for (uint32_t i = 0; i < to_copy; ++i) {
        dest[i] = rb->data[idx];
        idx = (idx + 1u) % RING_BUFFER_CAPACITY;
    }
    return to_copy;
}
