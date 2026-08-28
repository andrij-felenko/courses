#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    int n;
    int words_per_row;
    uint64_t *rows;
} BitsetWarshall;

BitsetWarshall* bitset_fw_create(int n) {
    BitsetWarshall *bw = (BitsetWarshall*)malloc(sizeof(BitsetWarshall));
    if (!bw) return NULL;
    bw->n = n;
    bw->words_per_row = (n + 63) / 64;
    bw->rows = (uint64_t*)calloc((size_t)n * bw->words_per_row, sizeof(uint64_t));
    if (!bw->rows) {
        free(bw);
        return NULL;
    }
    for (int i = 0; i < n; ++i) {
        bw->rows[i * bw->words_per_row + (i / 64)] |= (1ULL << (i % 64));
    }
    return bw;
}

void bitset_fw_add_edge(BitsetWarshall *bw, int u, int v) {
    if (u >= 0 && u < bw->n && v >= 0 && v < bw->n) {
        bw->rows[u * bw->words_per_row + (v / 64)] |= (1ULL << (v % 64));
    }
}

void bitset_fw_compute(BitsetWarshall *bw) {
    int n = bw->n;
    int w = bw->words_per_row;
    uint64_t *r = bw->rows;
    
    for (int k = 0; k < n; ++k) {
        int k_word = k / 64;
        uint64_t k_mask = (1ULL << (k % 64));
        uint64_t *row_k = &r[k * w];
        
        for (int i = 0; i < n; ++i) {
            uint64_t *row_i = &r[i * w];
            if (row_i[k_word] & k_mask) {
                for (int m = 0; m < w; ++m) {
                    row_i[m] |= row_k[m];
                }
            }
        }
    }
}

bool bitset_fw_reachable(const BitsetWarshall *bw, int u, int v) {
    if (u < 0 || u >= bw->n || v < 0 || v >= bw->n) return false;
    return (bw->rows[u * bw->words_per_row + (v / 64)] & (1ULL << (v % 64))) != 0;
}

void bitset_fw_destroy(BitsetWarshall *bw) {
    if (!bw) return;
    free(bw->rows);
    free(bw);
}
