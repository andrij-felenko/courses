#include <stdatomic.h>
#include <stdint.h>

#define FIFO_SIZE 256u
#define FIFO_MASK (FIFO_SIZE - 1u)

typedef struct {
    uint8_t              buf[FIFO_SIZE];
    _Atomic uint16_t     head;
    _Atomic uint16_t     tail;
} fifo_mc_t;

// Продюсер на своєму ядрі.
int fifo_put_mc(fifo_mc_t *q, uint8_t byte)
{
    uint16_t h = atomic_load_explicit(&q->head, memory_order_relaxed); // свій — relaxed
    uint16_t n = (uint16_t)((h + 1u) & FIFO_MASK);
    // чужий (хвіст) — acquire: побачити місце, звільнене споживачем
    if (n == atomic_load_explicit(&q->tail, memory_order_acquire))
        return 0;                       // повно
    q->buf[h] = byte;                   // дані у слот
    // публікуємо голову з release: дані гарантовано ляжуть ДО того,
    // як інше ядро побачить нову голову
    atomic_store_explicit(&q->head, n, memory_order_release);
    return 1;
}

// Споживач на іншому ядрі.
int fifo_get_mc(fifo_mc_t *q, uint8_t *out)
{
    uint16_t t = atomic_load_explicit(&q->tail, memory_order_relaxed); // свій — relaxed
    // чужий (голова) — acquire: парний до release продюсера
    if (t == atomic_load_explicit(&q->head, memory_order_acquire))
        return 0;                       // порожньо
    *out = q->buf[t];                   // читаємо дані (після acquire — вже видимі)
    // звільняємо слот із release: споживач опублікував «місце вільне»
    atomic_store_explicit(&q->tail, (uint16_t)((t + 1u) & FIFO_MASK),
                          memory_order_release);
    return 1;
}
