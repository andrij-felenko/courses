/* Квадратне спарювання Шудзіка (Elegant Pairing) */
uint64_t szudzik_encode(uint32_t x, uint32_t y) {
    uint64_t ux = x;
    uint64_t uy = y;
    if (ux < uy) {
        return uy * uy + ux;
    } else {
        return ux * ux + ux + uy;
    }
}

cantor_pair32_t szudzik_decode(uint64_t code) {
    uint64_t s = isqrt64_fast(code);
    uint64_t sq = s * s;
    uint64_t diff = code - sq;
    cantor_pair32_t p;

    if (diff < s) {
        p.x = (uint32_t)diff;
        p.y = (uint32_t)s;
    } else {
        p.x = (uint32_t)s;
        p.y = (uint32_t)(diff - s);
    }
    return p;
}

/* Кодування Мортона (Z-order curve) для 16-бітних координат у 32-бітний хеш */
uint32_t morton2d_encode16(uint16_t x, uint16_t y) {
    uint32_t x32 = x;
    uint32_t y32 = y;

    /* Рознесення бітів числа x: кожні 1 біт через 1 */
    x32 = (x32 | (x32 << 8)) & 0x00FF00FF;
    x32 = (x32 | (x32 << 4)) & 0x0F0F0F0F;
    x32 = (x32 | (x32 << 2)) & 0x33333333;
    x32 = (x32 | (x32 << 1)) & 0x55555555;

    /* Рознесення бітів числа y */
    y32 = (y32 | (y32 << 8)) & 0x00FF00FF;
    y32 = (y32 | (y32 << 4)) & 0x0F0F0F0F;
    y32 = (y32 | (y32 << 2)) & 0x33333333;
    y32 = (y32 | (y32 << 1)) & 0x55555555;

    return x32 | (y32 << 1);
}
