#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// Розмір буфера телеметрії — рівно ступінь двійки
#define TELEMETRY_BUF_SIZE 256U
#define TELEMETRY_BUF_MASK (TELEMETRY_BUF_SIZE - 1U)

// Перевірка на етапі компіляції (C11)
_Static_assert((TELEMETRY_BUF_SIZE & TELEMETRY_BUF_MASK) == 0, 
               "Розмір буфера мусить бути ступенем двійки!");

typedef struct {
    uint8_t buffer[TELEMETRY_BUF_SIZE];
    volatile uint16_t head; // Змінюється лише перериванням (Producer)
    volatile uint16_t tail; // Змінюється лише головним циклом (Consumer)
} RingBuffer;

void ring_buffer_init(RingBuffer *rb) {
    rb->head = 0;
    rb->tail = 0;
}

bool ring_buffer_is_empty(const RingBuffer *rb) {
    return rb->head == rb->tail;
}

bool ring_buffer_is_full(const RingBuffer *rb) {
    return ((rb->head + 1U) & TELEMETRY_BUF_MASK) == rb->tail;
}

uint16_t ring_buffer_available(const RingBuffer *rb) {
    return (uint16_t)((rb->head - rb->tail) & TELEMETRY_BUF_MASK);
}

bool ring_buffer_put(RingBuffer *rb, uint8_t byte) {
    uint16_t next_head = (uint16_t)((rb->head + 1U) & TELEMETRY_BUF_MASK);
    if (next_head == rb->tail) {
        return false; // Буфер переповнено, байт відкинуто
    }
    rb->buffer[rb->head] = byte;
    rb->head = next_head; // Атомарне оновлення покажчика
    return true;
}

bool ring_buffer_get(RingBuffer *rb, uint8_t *byte) {
    if (rb->head == rb->tail) {
        return false; // Буфер порожній
    }
    *byte = rb->buffer[rb->tail];
    rb->tail = (uint16_t)((rb->tail + 1U) & TELEMETRY_BUF_MASK);
    return true;
}
