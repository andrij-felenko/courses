#include <stdint.h>
#include <stddef.h>

// Розмір — ОБОВ'ЯЗКОВО степінь двійки: тоді обгортання індексу — це
// швидка маска & (SIZE-1), а не дороге ділення % SIZE.
#define FIFO_SIZE   256u
#define FIFO_MASK   (FIFO_SIZE - 1u)

typedef struct {
    uint8_t          buf[FIFO_SIZE];
    volatile uint16_t head;   // куди пише продюсер (ISR)
    volatile uint16_t tail;   // звідки читає споживач (main)
} fifo_t;

static inline void fifo_init(fifo_t *q)
{
    q->head = 0;
    q->tail = 0;
}

// Наступний індекс по колу. Маска замість % — див. нижче про степінь двійки.
static inline uint16_t fifo_next(uint16_t i)
{
    return (uint16_t)((i + 1u) & FIFO_MASK);
}

// «Порожньо» бачить споживач: голова наздогнала хвіст.
static inline int fifo_empty(const fifo_t *q)
{
    return q->head == q->tail;
}

// «Повно» бачить продюсер: наступна голова вперлась би в хвіст
// (пожертвувана комірка-роздільник).
static inline int fifo_full(const fifo_t *q)
{
    return fifo_next(q->head) == q->tail;
}
