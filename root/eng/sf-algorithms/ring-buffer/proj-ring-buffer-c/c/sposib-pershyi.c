#define RB1_CAP 256u                /* розмір масиву; корисна місткість — 255! */

typedef struct {
    uint8_t data[RB1_CAP];
    size_t  head;                   /* куди писати; завжди 0…RB1_CAP−1 */
    size_t  tail;                   /* звідки читати; завжди 0…RB1_CAP−1 */
} rb1_t;

static inline void rb1_init(rb1_t *r) { r->head = 0; r->tail = 0; }

static inline bool rb1_empty(const rb1_t *r) { return r->head == r->tail; }

static inline bool rb1_full(const rb1_t *r) {
    return ((r->head + 1u) % RB1_CAP) == r->tail;
}

static inline size_t rb1_count(const rb1_t *r) {
    return (r->head - r->tail + RB1_CAP) % RB1_CAP;
}

bool rb1_push(rb1_t *r, uint8_t x) {
    size_t next = (r->head + 1u) % RB1_CAP;
    if (next == r->tail) return false;      /* повно — одна комірка лишається вільною */
    r->data[r->head] = x;
    r->head = next;
    return true;
}

bool rb1_pop(rb1_t *r, uint8_t *out) {
    if (r->head == r->tail) return false;   /* порожньо */
    *out = r->data[r->tail];
    r->tail = (r->tail + 1u) % RB1_CAP;
    return true;
}
