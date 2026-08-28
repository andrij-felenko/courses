/* Реалізація мовою C: плоский масив 1D для двовимірної сітки (Row-Major Ordering) */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    int64_t* pref;
    size_t rows;
    size_t cols;
} PrefixSum2D;

static inline size_t idx2d(size_t r, size_t c, size_t stride_cols) {
    return r * stride_cols + c;
}

bool prefix_sum_2d_init(PrefixSum2D* ps, const int32_t* matrix, size_t rows, size_t cols) {
    if (!ps || !matrix || rows == 0 || cols == 0) return false;
    
    size_t p_cols = cols + 1;
    size_t p_rows = rows + 1;
    
    ps->pref = (int64_t*)calloc(p_rows * p_cols, sizeof(int64_t));
    if (!ps->pref) return false;
    
    ps->rows = rows;
    ps->cols = cols;
    
    for (size_t r = 0; r < rows; ++r) {
        for (size_t c = 0; c < cols; ++c) {
            int64_t val = (int64_t)matrix[r * cols + c];
            int64_t top = ps->pref[idx2d(r, c + 1, p_cols)];
            int64_t left = ps->pref[idx2d(r + 1, c, p_cols)];
            int64_t top_left = ps->pref[idx2d(r, c, p_cols)];
            
            ps->pref[idx2d(r + 1, c + 1, p_cols)] = val + top + left - top_left;
        }
    }
    return true;
}

int64_t prefix_sum_2d_query(const PrefixSum2D* ps, size_t r1, size_t c1, size_t r2, size_t c2) {
    if (!ps || !ps->pref || r1 > r2 || c1 > c2 || r2 >= ps->rows || c2 >= ps->cols) {
        return 0;
    }
    size_t p_cols = ps->cols + 1;
    
    int64_t total    = ps->pref[idx2d(r2 + 1, c2 + 1, p_cols)];
    int64_t top      = ps->pref[idx2d(r1, c2 + 1, p_cols)];
    int64_t left     = ps->pref[idx2d(r2 + 1, c1, p_cols)];
    int64_t top_left = ps->pref[idx2d(r1, c1, p_cols)];
    
    return total - top - left + top_left;
}

void prefix_sum_2d_free(PrefixSum2D* ps) {
    if (ps && ps->pref) {
        free(ps->pref);
        ps->pref = NULL;
        ps->rows = ps->cols = 0;
    }
}
