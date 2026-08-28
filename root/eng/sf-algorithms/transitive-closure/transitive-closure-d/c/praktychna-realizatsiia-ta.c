#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    size_t vertices;
    size_t words_per_row;
    uint64_t *matrix;
} bitset_tc_t;

bitset_tc_t* bitset_tc_create(size_t v) {
    bitset_tc_t *g = (bitset_tc_t*)malloc(sizeof(bitset_tc_t));
    if (!g) return NULL;
    g->vertices = v;
    g->words_per_row = (v + 63) / 64;
    g->matrix = (uint64_t*)calloc(v * g->words_per_row, sizeof(uint64_t));
    if (!g->matrix) {
        free(g);
        return NULL;
    }
    return g;
}

void bitset_tc_compute(bitset_tc_t *g) {
    if (!g || !g->matrix) return;
    const size_t v = g->vertices;
    const size_t wpr = g->words_per_row;
    uint64_t *m = g->matrix;

    for (size_t k = 0; k < v; ++k) {
        size_t k_word = k / 64;
        uint64_t k_mask = (1ULL << (k % 64));

        for (size_t i = 0; i < v; ++i) {
            if ((m[i * wpr + k_word] & k_mask) != 0) {
                uint64_t *row_i = &m[i * wpr];
                const uint64_t *row_k = &m[k * wpr];
                for (size_t w = 0; w < wpr; ++w) {
                    row_i[w] |= row_k[w];
                }
            }
        }
    }
}
