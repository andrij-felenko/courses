#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    size_t rows;
    size_t cols;
    long long* tree; // Одновимірний масив для плоского представлення rows*cols
} fenwick_2d_t;

static inline size_t fenwick_2d_lsb(size_t i) {
    return i & (-i);
}

fenwick_2d_t* fenwick_2d_create(size_t rows, size_t cols) {
    fenwick_2d_t* ft = (fenwick_2d_t*)malloc(sizeof(fenwick_2d_t));
    if (!ft) return NULL;
    ft->rows = rows;
    ft->cols = cols;
    ft->tree = (long long*)calloc((rows + 1) * (cols + 1), sizeof(long long));
    if (!ft->tree) {
        free(ft);
        return NULL;
    }
    return ft;
}

void fenwick_2d_destroy(fenwick_2d_t* ft) {
    if (ft) {
        free(ft->tree);
        free(ft);
    }
}

#define TREE_2D_AT(ft, i, j) ((ft)->tree[(i) * ((ft)->cols + 1) + (j)])

bool fenwick_2d_add(fenwick_2d_t* ft, size_t r, size_t c, long long val) {
    if (!ft || r >= ft->rows || c >= ft->cols) return false;
    for (size_t i = r + 1; i <= ft->rows; i += fenwick_2d_lsb(i)) {
        for (size_t j = c + 1; j <= ft->cols; j += fenwick_2d_lsb(j)) {
            TREE_2D_AT(ft, i, j) += val;
        }
    }
    return true;
}

long long fenwick_2d_query_prefix(const fenwick_2d_t* ft, size_t r, size_t c) {
    if (!ft || r >= ft->rows || c >= ft->cols) return 0;
    long long sum = 0;
    for (size_t i = r + 1; i > 0; i -= fenwick_2d_lsb(i)) {
        for (size_t j = c + 1; j > 0; j -= fenwick_2d_lsb(j)) {
            sum += TREE_2D_AT(ft, i, j);
        }
    }
    return sum;
}

long long fenwick_2d_query_rect(const fenwick_2d_t* ft, size_t r1, size_t c1, size_t r2, size_t c2) {
    if (!ft || r1 > r2 || c1 > c2 || r2 >= ft->rows || c2 >= ft->cols) return 0;
    long long res = fenwick_2d_query_prefix(ft, r2, c2);
    if (r1 > 0) res -= fenwick_2d_query_prefix(ft, r1 - 1, c2);
    if (c1 > 0) res -= fenwick_2d_query_prefix(ft, r2, c1 - 1);
    if (r1 > 0 && c1 > 0) res += fenwick_2d_query_prefix(ft, r1 - 1, c1 - 1);
    return res;
}
