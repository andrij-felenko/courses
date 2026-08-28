#include <stdint.h>
#include <stddef.h>

#define RB_SIZE 256u                 // степінь двійки → швидка маска
#define RB_MASK (RB_SIZE - 1u)

typedef struct {
    uint8_t  buf[RB_SIZE];
    volatile uint16_t head;          // writer index
    volatile uint16_t tail;          // reader index
    volatile uint16_t count;         // зайнято байтів
} ring_t;

static inline void rb_init(ring_t *r) {
    r->head = r->tail = r->count = 0;
}

// writer: 1 = записано, 0 = повно (політика «відкинути новий»)
static inline int rb_push(ring_t *r, uint8_t b) {
    if (r->count == RB_SIZE) return 0;     // повно
    r->buf[r->head] = b;                   // 1) дані
    r->head = (r->head + 1u) & RB_MASK;    // 2) посунути голову
    r->count++;
    return 1;
}

// reader: 1 = є байт (в *out), 0 = порожньо
static inline int rb_pop(ring_t *r, uint8_t *out) {
    if (r->count == 0u) return 0;          // порожньо
    *out = r->buf[r->tail];
    r->tail = (r->tail + 1u) & RB_MASK;
    r->count--;
    return 1;
}
