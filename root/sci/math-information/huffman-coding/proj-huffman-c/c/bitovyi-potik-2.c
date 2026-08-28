typedef struct {
    const uint8_t *buf;
    size_t cap, pos;
    uint32_t acc;
    int nbits;
} bitr_t;

static void br_init(bitr_t *r, const uint8_t *buf, size_t cap) {
    r->buf = buf; r->cap = cap; r->pos = 0; r->acc = 0; r->nbits = 0;
}

static void br_fill(bitr_t *r) {                       /* підкачати до >=24 біт */
    while (r->nbits <= 24 && r->pos < r->cap) {
        r->acc |= (uint32_t)r->buf[r->pos++] << (24 - r->nbits);
        r->nbits += 8;
    }
}

static uint32_t br_peek(bitr_t *r, int n) {            /* глянути n біт, не споживаючи */
    br_fill(r);
    return r->acc >> (32 - n);
}

static void br_skip(bitr_t *r, int n) {                /* спожити n біт */
    r->acc <<= n;
    r->nbits -= n;
}
