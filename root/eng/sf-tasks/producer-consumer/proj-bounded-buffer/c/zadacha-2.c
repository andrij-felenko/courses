#include <stdatomic.h>
#include <stdbool.h>
#include <stdlib.h>
#include <stddef.h>

// Вирівнювання структури під розмір кеш-лінії x86/ARM (64 байти)
typedef struct {
    // Кеш-лінія виробника
    _Alignas(64) atomic_size_t tail;
    size_t cached_head;

    // Кеш-лінія споживача
    _Alignas(64) atomic_size_t head;
    size_t cached_tail;

    // Спільні незмінні метадані та буфер
    _Alignas(64) size_t capacity;
    size_t mask;
    void** buffer;
} SpscRingBufferC;

SpscRingBufferC* spsc_create(size_t power_of_two_capacity) {
    // Перевірка, що capacity є степенем двійки
    if (power_of_two_capacity < 2 || (power_of_two_capacity & (power_of_two_capacity - 1)) != 0) {
        return NULL;
    }

    SpscRingBufferC* ring = (SpscRingBufferC*)malloc(sizeof(SpscRingBufferC));
    if (!ring) return NULL;

    ring->buffer = (void**)malloc(sizeof(void*) * power_of_two_capacity);
    if (!ring->buffer) {
        free(ring);
        return NULL;
    }

    ring->capacity = power_of_two_capacity;
    ring->mask = power_of_two_capacity - 1;
    atomic_init(&ring->tail, 0);
    atomic_init(&ring->head, 0);
    ring->cached_head = 0;
    ring->cached_tail = 0;
    return ring;
}

bool spsc_try_push(SpscRingBufferC* ring, void* item) {
    const size_t current_tail = atomic_load_explicit(&ring->tail, memory_order_relaxed);

    // Перевіряємо заповненість через локальну копію cached_head, щоб не смикати ядро споживача
    if (current_tail - ring->cached_head >= ring->capacity) {
        ring->cached_head = atomic_load_explicit(&ring->head, memory_order_acquire);
        if (current_tail - ring->cached_head >= ring->capacity) {
            return false; // Буфер переповнений
        }
    }

    ring->buffer[current_tail & ring->mask] = item;
    // Release гарантує, що запис даних у буфер завершився ДО оновлення індексу tail
    atomic_store_explicit(&ring->tail, current_tail + 1, memory_order_release);
    return true;
}

bool spsc_try_pop(SpscRingBufferC* ring, void** out_item) {
    const size_t current_head = atomic_load_explicit(&ring->head, memory_order_relaxed);

    if (current_head == ring->cached_tail) {
        ring->cached_tail = atomic_load_explicit(&ring->tail, memory_order_acquire);
        if (current_head == ring->cached_tail) {
            return false; // Буфер порожній
        }
    }

    *out_item = ring->buffer[current_head & ring->mask];
    // Release гарантує, що читання даних завершилося ДО оновлення індексу head
    atomic_store_explicit(&ring->head, current_head + 1, memory_order_release);
    return true;
}

void spsc_destroy(SpscRingBufferC* ring) {
    if (!ring) return;
    free(ring->buffer);
    free(ring);
}
