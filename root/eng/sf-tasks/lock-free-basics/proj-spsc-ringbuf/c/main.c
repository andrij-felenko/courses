#include <stdatomic.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define BUFFER_CAPACITY 1024 // Місткість обов'язково є степенем двійки
#define BUFFER_MASK (BUFFER_CAPACITY - 1)

typedef struct {
    // Масив даних фіксованого розміру
    int buffer[BUFFER_CAPACITY];

    // Розділення кеш-ліній для унеможливлення False Sharing (64 байти)
    _Alignas(64) _Atomic(size_t) head; // Модифікує тільки Producer
    _Alignas(64) _Atomic(size_t) tail; // Модифікує тільки Consumer
} SpscRingBuffer;

void spsc_init(SpscRingBuffer* q) {
    atomic_init(&q->head, 0);
    atomic_init(&q->tail, 0);
}

bool spsc_push(SpscRingBuffer* q, int item) {
    const size_t current_head = atomic_load_explicit(&q->head, memory_order_relaxed);
    const size_t current_tail = atomic_load_explicit(&q->tail, memory_order_acquire);

    // Перевірка на переповнення буфера
    if ((current_head - current_tail) >= BUFFER_CAPACITY) {
        return false; // Буфер повністю заповнений
    }

    // Запис елемента у відкриту комірку
    q->buffer[current_head & BUFFER_MASK] = item;

    // Публікація нового head через release
    atomic_store_explicit(&q->head, current_head + 1, memory_order_release);
    return true;
}

bool spsc_pop(SpscRingBuffer* q, int* item) {
    const size_t current_tail = atomic_load_explicit(&q->tail, memory_order_relaxed);
    const size_t current_head = atomic_load_explicit(&q->head, memory_order_acquire);

    // Перевірка на наявність даних
    if (current_tail == current_head) {
        return false; // Буфер порожній
    }

    // Зчитування елемента з комірки
    *item = q->buffer[current_tail & BUFFER_MASK];

    // Публікація звільнення комірки через release
    atomic_store_explicit(&q->tail, current_tail + 1, memory_order_release);
    return true;
}
