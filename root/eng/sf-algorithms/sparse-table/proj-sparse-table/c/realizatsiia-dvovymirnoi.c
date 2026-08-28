#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    size_t rows;
    size_t cols;
    size_t kx;
    size_t ky;
    int32_t *data; /* 4D масив, сплощений у 1D: kx * ky * rows * cols */
} sparse_table_2d_t;

static inline size_t st2d_log2(size_t x) {
    return (size_t)(31 - __builtin_clz((uint32_t)x));
}

static inline int32_t st2d_min(int32_t a, int32_t b) {
    return (a < b) ? a : b;
}

/* Макрос для 4D індексації */
#define ST2D_IDX(st, jx, jy, x, y) \
    ((((jx) * (st)->ky + (jy)) * (st)->rows + (x)) * (st)->cols + (y))

sparse_table_2d_t *st2d_create(const int32_t *matrix, size_t rows, size_t cols) {
    if (matrix == NULL || rows == 0 || cols == 0) return NULL;

    sparse_table_2d_t *st = (sparse_table_2d_t *)malloc(sizeof(sparse_table_2d_t));
    if (!st) return NULL;

    st->rows = rows;
    st->cols = cols;
    st->kx = st2d_log2(rows) + 1;
    st->ky = st2d_log2(cols) + 1;

    size_t total_size = st->kx * st->ky * rows * cols;
    st->data = (int32_t *)malloc(total_size * sizeof(int32_t));
    if (!st->data) {
        free(st);
        return NULL;
    }

    /* Базовий рівень jx=0, jy=0 */
    for (size_t x = 0; x < rows; ++x) {
        for (size_t y = 0; y < cols; ++y) {
            st->data[ST2D_IDX(st, 0, 0, x, y)] = matrix[x * cols + y];
        }
    }

    /* Побудова по виміру y для jx=0 */
    for (size_t jy = 1; jy < st->ky; ++jy) {
        size_t half_y = (size_t)1 << (jy - 1);
        for (size_t x = 0; x < rows; ++x) {
            for (size_t y = 0; y + ((size_t)1 << jy) <= cols; ++y) {
                st->data[ST2D_IDX(st, 0, jy, x, y)] = st2d_min(
                    st->data[ST2D_IDX(st, 0, jy - 1, x, y)],
                    st->data[ST2D_IDX(st, 0, jy - 1, x, y + half_y)]
                );
            }
        }
    }

    /* Побудова по виміру x для всіх jy */
    for (size_t jx = 1; jx < st->kx; ++jx) {
        size_t half_x = (size_t)1 << (jx - 1);
        for (size_t jy = 0; jy < st->ky; ++jy) {
            for (size_t x = 0; x + ((size_t)1 << jx) <= rows; ++x) {
                for (size_t y = 0; y < cols; ++y) {
                    st->data[ST2D_IDX(st, jx, jy, x, y)] = st2d_min(
                        st->data[ST2D_IDX(st, jx - 1, jy, x, y)],
                        st->data[ST2D_IDX(st, jx - 1, jy, x + half_x, y)]
                    );
                }
            }
        }
    }

    return st;
}

bool st2d_query(const sparse_table_2d_t *st, size_t x1, size_t y1, size_t x2, size_t y2, int32_t *res) {
    if (!st || !res || x1 > x2 || y1 > y2 || x2 >= st->rows || y2 >= st->cols) return false;

    size_t kx = st2d_log2(x2 - x1 + 1);
    size_t ky = st2d_log2(y2 - y1 + 1);

    size_t shift_x = (size_t)1 << kx;
    size_t shift_y = (size_t)1 << ky;

    int32_t top_left     = st->data[ST2D_IDX(st, kx, ky, x1, y1)];
    int32_t bottom_left  = st->data[ST2D_IDX(st, kx, ky, x2 - shift_x + 1, y1)];
    int32_t top_right    = st->data[ST2D_IDX(st, kx, ky, x1, y2 - shift_y + 1)];
    int32_t bottom_right = st->data[ST2D_IDX(st, kx, ky, x2 - shift_x + 1, y2 - shift_y + 1)];

    *res = st2d_min(st2d_min(top_left, bottom_left), st2d_min(top_right, bottom_right));
    return true;
}

void st2d_destroy(sparse_table_2d_t *st) {
    if (st) {
        free(st->data);
        free(st);
    }
}
