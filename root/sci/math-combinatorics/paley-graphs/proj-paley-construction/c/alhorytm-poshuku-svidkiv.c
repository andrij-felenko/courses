/* Бітовий пошук свідка z для множин U та W */
int32_t paley_find_extension_witness(const PaleyGraphC *g,
                                     const uint32_t *U, uint32_t s,
                                     const uint32_t *W, uint32_t t) {
    uint64_t *mask = (uint64_t*)malloc(g->words_per_row * sizeof(uint64_t));
    if (!mask) return -1;

    /* Початково всі вершини є кандидатами */
    memset(mask, 0xFF, g->words_per_row * sizeof(uint64_t));

    /* Очищення бітів за межами графа у останньому слові */
    uint32_t rem = g->p % 64;
    if (rem != 0) {
        mask[g->words_per_row - 1] = ((uint64_t)1 << rem) - 1;
    }

    /* 1. Накладання умови суміжності з усіма u in U */
    for (uint32_t i = 0; i < s; ++i) {
        uint32_t offset = U[i] * g->words_per_row;
        for (uint32_t w = 0; w < g->words_per_row; ++w) {
            mask[w] &= g->adj[offset + w];
        }
    }

    /* 2. Накладання умови несуміжності з усіма w in W */
    for (uint32_t j = 0; j < t; ++j) {
        uint32_t offset = W[j] * g->words_per_row;
        for (uint32_t w = 0; w < g->words_per_row; ++w) {
            mask[w] &= ~g->adj[offset + w];
        }
    }

    /* 3. Видалення самих елементів U та W із кандидатів */
    for (uint32_t i = 0; i < s; ++i) {
        mask[U[i] / 64] &= ~((uint64_t)1 << (U[i] % 64));
    }
    for (uint32_t j = 0; j < t; ++j) {
        mask[W[j] / 64] &= ~((uint64_t)1 << (W[j] % 64));
    }

    /* 4. Пошук першого встановленого біта */
    for (uint32_t w = 0; w < g->words_per_row; ++w) {
        if (mask[w] != 0) {
            int tz = __builtin_ctzll(mask[w]);
            int32_t witness = (int32_t)(w * 64 + tz);
            free(mask);
            return witness;
        }
    }

    free(mask);
    return -1; /* Свідка не існує */
}
