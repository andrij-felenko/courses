#include <stdatomic.h>
#include <stdalign.h>

#define SPSC_CAP  1024u
#define SPSC_MASK (SPSC_CAP - 1u)
#define CACHELINE 64

typedef struct {
    alignas(CACHELINE) _Atomic uint32_t head;   /* пише ЛИШЕ виробник */
    alignas(CACHELINE) _Atomic uint32_t tail;   /* пише ЛИШЕ споживач */
    alignas(CACHELINE) uint8_t data[SPSC_CAP];
} spsc_t;

/* Викликати ЛИШЕ з потоку-виробника. */
bool spsc_push(spsc_t *q, uint8_t x) {
    uint32_t h = atomic_load_explicit(&q->head, memory_order_relaxed);  /* свій — relaxed */
    uint32_t t = atomic_load_explicit(&q->tail, memory_order_acquire);  /* чужий — acquire */
    if ((uint32_t)(h - t) == SPSC_CAP) return false;                    /* повно */
    q->data[h & SPSC_MASK] = x;                                         /* 1. дані */
    atomic_store_explicit(&q->head, h + 1u, memory_order_release);      /* 2. публікація */
    return true;
}

/* Викликати ЛИШЕ з потоку-споживача. */
bool spsc_pop(spsc_t *q, uint8_t *out) {
    uint32_t t = atomic_load_explicit(&q->tail, memory_order_relaxed);  /* свій — relaxed */
    uint32_t h = atomic_load_explicit(&q->head, memory_order_acquire);  /* чужий — acquire */
    if (h == t) return false;                                           /* порожньо */
    *out = q->data[t & SPSC_MASK];                                      /* 1. дані */
    atomic_store_explicit(&q->tail, t + 1u, memory_order_release);      /* 2. звільнення */
    return true;
}
