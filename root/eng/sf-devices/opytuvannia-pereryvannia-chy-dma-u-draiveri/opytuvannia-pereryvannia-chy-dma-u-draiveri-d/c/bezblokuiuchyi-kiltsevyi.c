#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define RING_BUFFER_SIZE 256  // Обов'язково ступінь двійки
#define RING_BUFFER_MASK (RING_BUFFER_SIZE - 1)

typedef struct {
    uint8_t storage[RING_BUFFER_SIZE];
    volatile uint32_t head;  // Модифікується лише виробником (ISR)
    volatile uint32_t tail;  // Модифікується лише споживачем (Thread)
} RingBufferSPSC_t;

static inline void RingBuffer_Init(RingBufferSPSC_t *rb) {
    rb->head = 0;
    rb->tail = 0;
}

static inline bool RingBuffer_PutFromISR(RingBufferSPSC_t *rb, uint8_t byte) {
    uint32_t current_head = rb->head;
    uint32_t current_tail = rb->tail;

    // Перевірка переповнення
    if (((current_head + 1) & RING_BUFFER_MASK) == (current_tail & RING_BUFFER_MASK)) {
        return false; // Буфер переповнено, байт втрачено
    }

    rb->storage[current_head & RING_BUFFER_MASK] = byte;
    
    // Апаратний бар'єр пам'яті гарантує, що запис у буфер завершиться ДО оновлення head
    __asm volatile ("dmb" ::: "memory");
    rb->head = current_head + 1;
    return true;
}

static inline bool RingBuffer_Get(RingBufferSPSC_t *rb, uint8_t *byte) {
    uint32_t current_head = rb->head;
    uint32_t current_tail = rb->tail;

    if (current_head == current_tail) {
        return false; // Буфер порожній
    }

    *byte = rb->storage[current_tail & RING_BUFFER_MASK];
    __asm volatile ("dmb" ::: "memory");
    rb->tail = current_tail + 1;
    return true;
}

static inline size_t RingBuffer_Available(const RingBufferSPSC_t *rb) {
    uint32_t current_head = rb->head;
    uint32_t current_tail = rb->tail;
    return (size_t)(current_head - current_tail);
}
