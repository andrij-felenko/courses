#include <stdint.h>
#include <stdbool.h>

#define FIFO_SIZE 128
#define FIFO_MASK (FIFO_SIZE - 1)

typedef struct {
    uint8_t buffer[FIFO_SIZE];
    volatile uint32_t head;
    volatile uint32_t tail;
} FastFifo_t;

bool FastFifo_Put(FastFifo_t *f, uint8_t byte) {
    uint32_t h = f->head;
    if (((h + 1) & FIFO_MASK) == (f->tail & FIFO_MASK)) return false;
    f->buffer[h & FIFO_MASK] = byte;
    __asm volatile ("dmb" ::: "memory");
    f->head = h + 1;
    return true;
}
