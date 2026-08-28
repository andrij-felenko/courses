#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <pthread.h>
#include <sched.h>
#include <string.h>

#define CACHELINE_SIZE 64
#define RING_CAPACITY 1024  /* Має бути степенем двійки */
#define RING_MASK (RING_CAPACITY - 1)

/* Структура повідомлення між ядрами */
typedef struct {
    uint32_t sender_core;
    uint32_t message_id;
    uint64_t payload;
} cross_core_msg_t;

/* Вирівняний SPSC кільцевий буфер */
typedef struct {
    /* Зона споживача: модифікується лише споживачем */
    alignas(CACHELINE_SIZE) _Atomic size_t head;
    alignas(CACHELINE_SIZE) size_t cached_tail; /* Локальний кеш хвоста для споживача */

    /* Зона виробника: модифікується лише виробником */
    alignas(CACHELINE_SIZE) _Atomic size_t tail;
    alignas(CACHELINE_SIZE) size_t cached_head; /* Локальний кеш голови для виробника */

    /* Буфер даних */
    alignas(CACHELINE_SIZE) cross_core_msg_t buffer[RING_CAPACITY];
} spsc_ring_t;

/* Ініціалізація кільцевого буфера */
void spsc_init(spsc_ring_t *ring) {
    atomic_init(&ring->head, 0);
    atomic_init(&ring->tail, 0);
    ring->cached_head = 0;
    ring->cached_tail = 0;
}

/* Відправка одного повідомлення (Producer Core) */
bool spsc_push(spsc_ring_t *ring, const cross_core_msg_t *msg) {
    size_t current_tail = atomic_load_explicit(&ring->tail, memory_order_relaxed);
    
    /* Перевірка вільного місця з використанням кешованої голови */
    if (current_tail - ring->cached_head >= RING_CAPACITY) {
        ring->cached_head = atomic_load_explicit(&ring->head, memory_order_acquire);
        if (current_tail - ring->cached_head >= RING_CAPACITY) {
            return false; /* Буфер переповнений */
        }
    }

    /* Запис даних у кільцевий слот */
    ring->buffer[current_tail & RING_MASK] = *msg;
    
    /* Публікація оновленого хвоста з бар'єром release */
    atomic_store_explicit(&ring->tail, current_tail + 1, memory_order_release);
    return true;
}

/* Пакетоване вилучення повідомлень (Consumer Core) */
size_t spsc_pop_batch(spsc_ring_t *ring, cross_core_msg_t *out_msgs, size_t max_count) {
    size_t current_head = atomic_load_explicit(&ring->head, memory_order_relaxed);

    /* Перевірка наявності даних з використанням кешованого хвоста */
    if (current_head == ring->cached_tail) {
        ring->cached_tail = atomic_load_explicit(&ring->tail, memory_order_acquire);
        if (current_head == ring->cached_tail) {
            return 0; /* Буфер порожній */
        }
    }

    size_t available = ring->cached_tail - current_head;
    size_t to_read = (available < max_count) ? available : max_count;

    for (size_t i = 0; i < to_read; ++i) {
        out_msgs[i] = ring->buffer[(current_head + i) & RING_MASK];
    }

    /* Оновлення голови з бар'єром release для сповіщення виробника */
    atomic_store_explicit(&ring->head, current_head + to_read, memory_order_release);
    return to_read;
}

/* Прив'язка поточного потоку до фізичного ядра CPU */
bool pin_thread_to_core(int core_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);
    pthread_t current_thread = pthread_self();
    return pthread_setaffinity_np(current_thread, sizeof(cpu_set_t), &cpuset) == 0;
}
