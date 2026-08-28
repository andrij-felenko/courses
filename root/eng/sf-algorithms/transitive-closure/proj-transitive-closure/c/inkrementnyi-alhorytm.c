#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

void bitset_tc_add_edge_incremental(uint64_t *matrix, size_t V, size_t u, size_t v) {
    size_t wpr = (V + 63) / 64;
    size_t u_word = u * wpr + (v / 64);
    uint64_t v_mask = (1ULL << (v % 64));

    if ((matrix[u_word] & v_mask) != 0) return; // Ребро вже існувало

    matrix[u_word] |= v_mask;

    // Всі вершини i, з яких досяжна u, тепер бачать всі вершини j, досяжні з v
    for (size_t i = 0; i < V; ++i) {
        size_t i_u_word = i * wpr + (u / 64);
        uint64_t u_mask = (1ULL << (u % 64));

        if (i == u || (matrix[i_u_word] & u_mask) != 0) {
            uint64_t *row_i = &matrix[i * wpr];
            const uint64_t *row_v = &matrix[v * wpr];
            for (size_t w = 0; w < wpr; ++w) {
                row_i[w] |= row_v[w];
            }
        }
    }
}
