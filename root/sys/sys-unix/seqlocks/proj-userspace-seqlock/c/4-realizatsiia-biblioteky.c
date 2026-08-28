/* Реалізація на мові C (стандарт C11 stdatomic.h) */
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <pthread.h>

typedef struct {
    _Alignas(64) _Atomic uint32_t seq;   /* лічильник вирівняно на межу кеш-лінії (§2) */
    pthread_spinlock_t writer_spin;
} seqlock_t;

static inline void seqlock_init(seqlock_t *sl)
{
    atomic_init(&sl->seq, 0);
    pthread_spin_init(&sl->writer_spin, PTHREAD_PROCESS_PRIVATE);
}

static inline void seqlock_destroy(seqlock_t *sl)
{
    pthread_spin_destroy(&sl->writer_spin);
}

static inline void seqlock_write_begin(seqlock_t *sl)
{
    pthread_spin_lock(&sl->writer_spin);
    uint32_t s = atomic_load_explicit(&sl->seq, memory_order_relaxed);
    atomic_store_explicit(&sl->seq, s + 1, memory_order_relaxed);
    /* аналог smp_wmb(): дані не можуть переїхати ПЕРЕД інкрементом лічильника */
    atomic_thread_fence(memory_order_release);
}

static inline void seqlock_write_end(seqlock_t *sl)
{
    uint32_t s = atomic_load_explicit(&sl->seq, memory_order_relaxed);
    atomic_store_explicit(&sl->seq, s + 1, memory_order_release);
    pthread_spin_unlock(&sl->writer_spin);
}

static inline uint32_t seqlock_read_begin(const seqlock_t *sl)
{
    uint32_t s;
    for (;;) {
        s = atomic_load_explicit((_Atomic uint32_t *)&sl->seq, memory_order_acquire);
        if ((s & 1U) == 0) {
            break;
        }
#if defined(__x86_64__) || defined(__i386__)
        __asm__ __volatile__("pause" ::: "memory");
#endif
    }
    return s;
}

static inline bool seqlock_read_retry(const seqlock_t *sl, uint32_t start_seq)
{
    atomic_thread_fence(memory_order_acquire);
    uint32_t current_seq = atomic_load_explicit((_Atomic uint32_t *)&sl->seq, memory_order_relaxed);
    return current_seq != start_seq;
}
