typedef struct { uint32_t bits; uint8_t len; } code_t;

static void canonical_codes(const uint8_t *len, code_t *code) {
    uint32_t bl_count[MAXLEN + 1] = {0};
    for (int s = 0; s < SYMS; s++)
        if (len[s]) bl_count[len[s]]++;

    uint32_t next[MAXLEN + 1] = {0};
    uint32_t c = 0;
    for (int bits = 1; bits <= MAXLEN; bits++) {        /* стартовий код довжини bits */
        c = (c + bl_count[bits - 1]) << 1;
        next[bits] = c;
    }
    for (int s = 0; s < SYMS; s++) {                    /* роздати по порядку символів */
        if (!len[s]) { code[s].len = 0; continue; }
        code[s].bits = next[len[s]]++;
        code[s].len  = len[s];
    }
}
