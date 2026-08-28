#include <string.h>

// забрати до n байтів суцільним блоком; повертає скільки реально віддав
static size_t rb_pop_block(ring_t *r, uint8_t *dst, size_t n) {
    if (n > r->count) n = r->count;        // не більше, ніж є
    size_t first = RB_SIZE - r->tail;      // до фізичного краю масиву
    if (first > n) first = n;
    memcpy(dst,         &r->buf[r->tail], first);    // частина 1: tail..край
    memcpy(dst + first, &r->buf[0],       n - first); // частина 2: з початку
    r->tail  = (r->tail + n) & RB_MASK;
    r->count -= (uint16_t)n;
    return n;
}
