typedef struct { int16_t sym; uint8_t len; } dentry_t;

size_t huff_decompress(const uint8_t *in, size_t n_in, uint8_t *out, size_t out_cap) {
    if (n_in < 4 + SYMS) return 0;
    size_t p = 0;
    size_t n = (size_t)in[p] | ((size_t)in[p+1] << 8)
             | ((size_t)in[p+2] << 16) | ((size_t)in[p+3] << 24);
    p += 4;
    uint8_t len[SYMS];
    memcpy(len, in + p, SYMS); p += SYMS;
    if (n == 0) return 0;

    code_t code[SYMS];
    canonical_codes(len, code);

    int maxbits = 1;
    for (int s = 0; s < SYMS; s++) if (len[s] > maxbits) maxbits = len[s];

    size_t tsize = (size_t)1 << maxbits;
    dentry_t *table = (dentry_t *)malloc(tsize * sizeof(dentry_t));
    if (!table) return 0;
    for (size_t i = 0; i < tsize; i++) { table[i].sym = -1; table[i].len = 0; }

    for (int s = 0; s < SYMS; s++) {                   /* розкласти кожен код по комірках */
        if (!len[s]) continue;
        int shift = maxbits - len[s];
        size_t base = (size_t)code[s].bits << shift;   /* старші біти = код, решта вільна */
        size_t cnt  = (size_t)1 << shift;
        for (size_t k = 0; k < cnt; k++) {
            table[base + k].sym = (int16_t)s;
            table[base + k].len = len[s];
        }
    }

    bitr_t r; br_init(&r, in + p, n_in - p);
    size_t produced = 0;
    while (produced < n && produced < out_cap) {
        uint32_t window = br_peek(&r, maxbits);
        dentry_t e = table[window];
        if (e.len == 0) break;                         /* пошкоджений потік — спинитися */
        out[produced++] = (uint8_t)e.sym;
        br_skip(&r, e.len);
    }
    free(table);
    return produced;
}
