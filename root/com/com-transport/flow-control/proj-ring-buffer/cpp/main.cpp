#include <stdint.h>
#include <stdbool.h>

#define RB_SIZE 256                 // степінь двійки → маска замість ділення
#define RB_MASK (RB_SIZE - 1)

typedef struct {
    volatile uint8_t  buf[RB_SIZE];
    volatile uint16_t head;         // пише ЛИШЕ переривання
    volatile uint16_t tail;         // пише ЛИШЕ читач
} RingBuf;

static inline bool rb_empty(const RingBuf* r) {
    return r->head == r->tail;
}

static inline bool rb_full(const RingBuf* r) {
    return ((r->head + 1) & RB_MASK) == r->tail;   // наступний head упреться в tail
}
