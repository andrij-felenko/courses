#ifndef SPSC_QUEUE_H
#define SPSC_QUEUE_H

#include <stdatomic.h>
#include <stdbool.h>
#include <string.h>

#include "guidance.h"

/* Черга детекцій між потоком зору і контуром керування.
 *
 * Один виробник, один споживач, без замків: контур реального часу не має
 * права заснути на м'ютексі, який захопив потік зору, — саме так з'являються
 * пропущені такти таймера. Місткість — степінь двійки, індекси не скидаються
 * і обгортаються маскою.
 *
 * Черга свідомо коротка: детекція, що пролежала півсекунди, все одно нікому
 * не потрібна, а глибока черга лише ховала б проблему. */
#define DETQ_CAPACITY 16u
#define DETQ_MASK (DETQ_CAPACITY - 1u)

typedef struct {
    TargetDetection  slots[DETQ_CAPACITY];
    _Atomic unsigned head;      /* читає й пише споживач */
    _Atomic unsigned tail;      /* читає й пише виробник */
    _Atomic unsigned dropped;
} DetectionQueue;

static inline void detq_init(DetectionQueue *q)
{
    memset(q->slots, 0, sizeof(q->slots));
    atomic_init(&q->head, 0u);
    atomic_init(&q->tail, 0u);
    atomic_init(&q->dropped, 0u);
}

/* Викликає ЛИШЕ потік зору. */
static inline bool detq_push(DetectionQueue *q, const TargetDetection *det)
{
    const unsigned tail = atomic_load_explicit(&q->tail, memory_order_relaxed);
    const unsigned head = atomic_load_explicit(&q->head, memory_order_acquire);

    if (tail - head >= DETQ_CAPACITY) {
        /* Черга повна — контур керування стоїть. Ховати це не можна:
         * лічильник утрат іде в телеметрію. */
        atomic_fetch_add_explicit(&q->dropped, 1u, memory_order_relaxed);
        return false;
    }

    q->slots[tail & DETQ_MASK] = *det;
    /* release: запис слота мусить стати видимим ДО нового tail. */
    atomic_store_explicit(&q->tail, tail + 1u, memory_order_release);
    return true;
}

/* Викликає ЛИШЕ потік керування. */
static inline bool detq_pop(DetectionQueue *q, TargetDetection *out)
{
    const unsigned head = atomic_load_explicit(&q->head, memory_order_relaxed);
    const unsigned tail = atomic_load_explicit(&q->tail, memory_order_acquire);

    if (head == tail) {
        return false;
    }

    *out = q->slots[head & DETQ_MASK];
    atomic_store_explicit(&q->head, head + 1u, memory_order_release);
    return true;
}

static inline unsigned detq_dropped(const DetectionQueue *q)
{
    return atomic_load_explicit(&q->dropped, memory_order_relaxed);
}

#endif /* SPSC_QUEUE_H */
