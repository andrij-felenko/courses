#define RB2_CAP 256u

typedef struct {
    uint8_t data[RB2_CAP];
    size_t  head;
    size_t  tail;
    size_t  size;                   /* скільки елементів усередині просто зараз */
} rb2_t;

static inline void rb2_init(rb2_t *r) { r->head = 0; r->tail = 0; r->size = 0; }

bool rb2_push(rb2_t *r, uint8_t x) {
    if (r->size == RB2_CAP) return false;   /* повно */
    r->data[r->head] = x;
    r->head = (r->head + 1u) % RB2_CAP;
    r->size++;
    return true;
}

bool rb2_pop(rb2_t *r, uint8_t *out) {
    if (r->size == 0) return false;         /* порожньо */
    *out = r->data[r->tail];
    r->tail = (r->tail + 1u) % RB2_CAP;
    r->size--;
    return true;
}
