#include <stdatomic.h>
#include <stdbool.h>
#include <stddef.h>

#define CAPACITY 1024
#define MASK (CAPACITY - 1)

typedef struct {
    int buffer[CAPACITY];
    // Розділення кеш-ліній (64 байти) для усунення False Sharing
    _Alignas(64) _Atomic(size_t) head;
    _Alignas(64) _Atomic(size_t) tail;
} SpscQueue;

bool spsc_push(SpscQueue* q, int item) {
    size_t h = atomic_load_explicit(&q->head, memory_order_relaxed);
    size_t t = atomic_load_explicit(&q->tail, memory_order_acquire);

    if (h - t >= CAPACITY) return false; // Черга заповнена

    q->buffer[h & MASK] = item;
    atomic_store_explicit(&q->head, h + 1, memory_order_release);
    return true;
}

bool spsc_pop(SpscQueue* q, int* item) {
    size_t t = atomic_load_explicit(&q->tail, memory_order_relaxed);
    size_t h = atomic_load_explicit(&q->head, memory_order_acquire);

    if (t == h) return false; // Черга порожня

    *item = q->buffer[t & MASK];
    atomic_store_explicit(&q->tail, t + 1, memory_order_release);
    return true;
}
