#include <stdint.h>
#include <stdbool.h>

#define CAP  256                /* місткість — степінь двійки */
#define MASK (CAP - 1)

typedef struct {
    uint8_t  data[CAP];
    uint32_t head;              /* куди писати наступний елемент */
    uint32_t tail;              /* звідки читати наступний */
    uint32_t size;              /* скільки елементів зараз у буфері */
} ring_t;

bool ring_push(ring_t *r, uint8_t x) {
    if (r->size == CAP) return false;   /* повно — відмова */
    r->data[r->head & MASK] = x;
    r->head++;
    r->size++;
    return true;
}

bool ring_pop(ring_t *r, uint8_t *out) {
    if (r->size == 0) return false;     /* порожньо */
    *out = r->data[r->tail & MASK];
    r->tail++;
    r->size--;
    return true;
}
