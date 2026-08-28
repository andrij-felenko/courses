/* Рекурсивний пошук максимальної кліки методом Брона — Кербоша */
static void bron_kerbosch_pivot(const PaleyGraphC *g,
                                uint64_t *R, uint64_t *P, uint64_t *X,
                                uint32_t *max_clique_size) {
    /* Перевірка чи множини P та X є порожніми */
    bool p_empty = true, x_empty = true;
    for (uint32_t w = 0; w < g->words_per_row; ++w) {
        if (P[w] != 0) p_empty = false;
        if (X[w] != 0) x_empty = false;
    }

    if (p_empty && x_empty) {
        /* Знайдено максимальну кліку: рахуємо її розмір */
        uint32_t size = 0;
        for (uint32_t w = 0; w < g->words_per_row; ++w) {
            size += (uint32_t)__builtin_popcountll(R[w]);
        }
        if (size > *max_clique_size) *max_clique_size = size;
        return;
    }

    if (p_empty) return;

    /* Вибір півота u з P ∪ X для максимізації відсікання */
    uint32_t pivot = 0;
    for (uint32_t w = 0; w < g->words_per_row; ++w) {
        uint64_t union_px = P[w] | X[w];
        if (union_px != 0) {
            pivot = w * 64 + (uint32_t)__builtin_ctzll(union_px);
            break;
        }
    }

    /* Кандидати для перебору: P \ N(pivot) */
    uint64_t *candidates = (uint64_t*)malloc(g->words_per_row * sizeof(uint64_t));
    uint32_t pivot_offset = pivot * g->words_per_row;
    for (uint32_t w = 0; w < g->words_per_row; ++w) {
        candidates[w] = P[w] & ~g->adj[pivot_offset + w];
    }

    for (uint32_t w = 0; w < g->words_per_row; ++w) {
        while (candidates[w] != 0) {
            int bit = __builtin_ctzll(candidates[w]);
            uint32_t v = w * 64 + (uint32_t)bit;
            candidates[w] &= ~((uint64_t)1 << bit);

            /* Формування нових множин R_new, P_new, X_new */
            uint64_t *R_new = (uint64_t*)malloc(g->words_per_row * sizeof(uint64_t));
            uint64_t *P_new = (uint64_t*)malloc(g->words_per_row * sizeof(uint64_t));
            uint64_t *X_new = (uint64_t*)malloc(g->words_per_row * sizeof(uint64_t));
            uint32_t v_offset = v * g->words_per_row;

            for (uint32_t k = 0; k < g->words_per_row; ++k) {
                R_new[k] = R[k];
                P_new[k] = P[k] & g->adj[v_offset + k];
                X_new[k] = X[k] & g->adj[v_offset + k];
            }
            R_new[v / 64] |= ((uint64_t)1 << (v % 64));

            bron_kerbosch_pivot(g, R_new, P_new, X_new, max_clique_size);

            free(R_new);
            free(P_new);
            free(X_new);

            /* Переміщення v з P до X */
            P[v / 64] &= ~((uint64_t)1 << (v % 64));
            X[v / 64] |= ((uint64_t)1 << (v % 64));
        }
    }
    free(candidates);
}

uint32_t paley_compute_clique_number(const PaleyGraphC *g) {
    uint64_t *R = (uint64_t*)calloc(g->words_per_row, sizeof(uint64_t));
    uint64_t *P = (uint64_t*)malloc(g->words_per_row * sizeof(uint64_t));
    uint64_t *X = (uint64_t*)calloc(g->words_per_row, sizeof(uint64_t));

    memset(P, 0xFF, g->words_per_row * sizeof(uint64_t));
    uint32_t rem = g->p % 64;
    if (rem != 0) {
        P[g->words_per_row - 1] = ((uint64_t)1 << rem) - 1;
    }

    uint32_t max_clique = 0;
    bron_kerbosch_pivot(g, R, P, X, &max_clique);

    free(R);
    free(P);
    free(X);
    return max_clique;
}
