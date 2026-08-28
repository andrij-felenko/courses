// dst[·] ^= c · src[·]  над GF(256), по всій довжині L.
// Разова таблиця множення на фіксований c → у циклі лише вибірка + XOR.
static void gf_mul_add(uint8_t *dst, const uint8_t *src, uint8_t c, size_t L) {
    if (c == 0) return;                       // множення на 0 нічого не додає
    uint8_t mulc[256];
    mulc[0] = 0;
    int lc = gf_log[c];
    for (int x = 1; x < 256; x++)
        mulc[x] = gf_exp[gf_log[x] + lc];     // mulc[x] = c·x
    for (size_t i = 0; i < L; i++)
        dst[i] ^= mulc[src[i]];               // гарячий цикл: вибірка + XOR
}

// Кодер: k пакетів даних data[0..k-1] по L байтів → m ремонтних repair[0..m-1].
void rs_encode(const uint8_t *data[], int k, int m, size_t L,
               const uint8_t *C, uint8_t *repair[]) {
    for (int i = 0; i < m; i++) {
        for (size_t b = 0; b < L; b++) repair[i][b] = 0;  // акумулятор
        for (int j = 0; j < k; j++)
            gf_mul_add(repair[i], data[j], C[i * k + j], L);
    }
}
