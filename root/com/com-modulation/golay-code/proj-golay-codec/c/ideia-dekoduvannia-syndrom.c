static inline int weight(uint32_t x) { return __builtin_popcount(x); }

/* Синдром s = B·x ⊕ y. Для симетричної B  B·x = x·B, тож — той самий XOR рядків. */
static uint16_t syndrome(uint32_t r) {
    uint16_t x = r & 0x0FFF;
    uint16_t y = (r >> 12) & 0x0FFF;
    return times_B(x) ^ y;
}

/* Патерн помилки e (24 біти) у *err; повертає 1, якщо виправлено,
   0 — якщо слово невиправне (4+ помилки). */
int golay_error(uint32_t r, uint32_t *err) {
    uint16_t s = syndrome(r);
    if (weight(s) <= 3) { *err = (uint32_t)s << 12; return 1; }
    for (int i = 0; i < 12; i++) {
        uint16_t t = s ^ B[i];
        if (weight(t) <= 2) { *err = (1u << i) | ((uint32_t)t << 12); return 1; }
    }
    uint16_t s2 = times_B(s);                 /* B·s, бо B² = I */
    if (weight(s2) <= 3) { *err = s2; return 1; }
    for (int i = 0; i < 12; i++) {
        uint16_t t = s2 ^ B[i];
        if (weight(t) <= 2) { *err = ((uint32_t)(1u << i) << 12) | t; return 1; }
    }
    return 0;                                 /* невиправно: 4+ помилки */
}

/* Виправлені 12 бітів даних у *data. Повертає 0, або -1, якщо невиправно. */
int golay_decode(uint32_t r, uint16_t *data) {
    uint32_t e;
    if (!golay_error(r, &e)) return -1;
    *data = (uint16_t)((r ^ e) & 0x0FFF);
    return 0;
}
