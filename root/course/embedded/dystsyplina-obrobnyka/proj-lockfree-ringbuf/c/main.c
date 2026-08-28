#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define RING_BUFFER_SIZE 128
#define RING_BUFFER_MASK (RING_BUFFER_SIZE - 1)

#if (RING_BUFFER_SIZE & RING_BUFFER_MASK) != 0
#error "RING_BUFFER_SIZE must be a power of two!"
#endif

typedef struct {
    uint8_t buffer[RING_BUFFER_SIZE];
    volatile uint32_t head;
    volatile uint32_t tail;
} spsc_ring_buffer_t;

void ring_buffer_init(spsc_ring_buffer_t *rb) {
    rb->head = 0;
    rb->tail = 0;
}

/* Викликається з ISR: записує байт, повертає false якщо буфер переповнено */
bool ring_buffer_push_isr(spsc_ring_buffer_t *rb, uint8_t byte) {
    uint32_t current_head = rb->head;
    uint32_t current_tail = rb->tail;
    uint32_t next_head = (current_head + 1) & RING_BUFFER_MASK;

    if (next_head == current_tail) {
        /* Буфер повний: переповнення (overrun) */
        return false;
    }

    rb->buffer[current_head] = byte;

    /* Бар'єр пам'яті DMB: гарантує, що запис байта в масив завершено
       ДО того, як нове значення head стане видимим для інших потоків */
    __asm volatile ("dmb" ::: "memory");

    rb->head = next_head;
    return true;
}

/* Викликається з основного потоку: вичитує байт */
bool ring_buffer_pop_main(spsc_ring_buffer_t *rb, uint8_t *byte) {
    uint32_t current_tail = rb->tail;
    uint32_t current_head = rb->head;

    if (current_tail == current_head) {
        /* Буфер порожній */
        return false;
    }

    *byte = rb->buffer[current_tail];

    /* Бар'єр пам'яті: байт прочитано до оновлення tail */
    __asm volatile ("dmb" ::: "memory");

    rb->tail = (current_tail + 1) & RING_BUFFER_MASK;
    return true;
}

/* Кількість елементів, доступних для читання */
size_t ring_buffer_available(const spsc_ring_buffer_t *rb) {
    uint32_t head = rb->head;
    uint32_t tail = rb->tail;
    return (head - tail) & RING_BUFFER_MASK;
}
