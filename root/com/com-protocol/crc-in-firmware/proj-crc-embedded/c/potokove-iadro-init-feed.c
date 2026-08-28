typedef struct { uint32_t reg; } crc32_ctx;

static inline void crc32_init(crc32_ctx *c) {
    c->reg = 0xFFFFFFFFU;                       /* старт профілю — РАЗ на весь потік */
}
static inline void crc32_feed(crc32_ctx *c, const uint8_t *p, size_t n) {
    c->reg = crc32_update(c->reg, p, n);        /* скільки завгодно разів, порціями будь-якого розміру */
}
static inline uint32_t crc32_final(const crc32_ctx *c) {
    return c->reg ^ 0xFFFFFFFFU;                /* фінальний XOR — РАЗ, після останнього байта */
}
