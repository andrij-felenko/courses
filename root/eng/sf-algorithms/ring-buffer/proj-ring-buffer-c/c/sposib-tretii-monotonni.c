#define RB3_CAP  256u                       /* СТЕПІНЬ ДВІЙКИ — не побажання, а умова */
#define RB3_MASK (RB3_CAP - 1u)

_Static_assert(RB3_CAP != 0u && (RB3_CAP & RB3_MASK) == 0u,
               "місткість мусить бути степенем двійки");

typedef struct {
    uint8_t  data[RB3_CAP];
    uint32_t head;                          /* СКІЛЬКИ ВСЬОГО покладено; не скидається */
    uint32_t tail;                          /* СКІЛЬКИ ВСЬОГО забрано */
} rb3_t;

static inline void     rb3_init(rb3_t *r)        { r->head = 0; r->tail = 0; }
static inline uint32_t rb3_count(const rb3_t *r) { return r->head - r->tail; }
static inline bool     rb3_empty(const rb3_t *r) { return r->head == r->tail; }
static inline bool     rb3_full(const rb3_t *r)  { return rb3_count(r) == RB3_CAP; }

bool rb3_push(rb3_t *r, uint8_t x) {
    if (rb3_count(r) == RB3_CAP) return false;
    r->data[r->head & RB3_MASK] = x;
    r->head++;
    return true;
}

bool rb3_pop(rb3_t *r, uint8_t *out) {
    if (r->head == r->tail) return false;
    *out = r->data[r->tail & RB3_MASK];
    r->tail++;
    return true;
}
