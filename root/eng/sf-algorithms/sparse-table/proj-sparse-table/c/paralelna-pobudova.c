#include <omp.h>
#include <stdlib.h>
#include <stdint.h>

/* Паралельна побудова таблиці з використанням OpenMP */
void st_build_parallel_omp(sparse_table_t *st, const int32_t *array) {
    size_t n = st->n;
    
    /* Рівень 0: паралельне копіювання */
    #pragma omp parallel for schedule(static)
    for (size_t i = 0; i < n; ++i) {
        st->data[0 * n + i] = array[i];
    }

    /* Рівні j >= 1: обчислюються послідовно по рівнях, але паралельно по елементах */
    for (size_t j = 1; j < st->levels; ++j) {
        size_t half = (size_t)1 << (j - 1);
        size_t len = (size_t)1 << j;
        size_t row_curr = j * n;
        size_t row_prev = (j - 1) * n;
        size_t limit = (n >= len) ? (n - len + 1) : 0;

        #pragma omp parallel for schedule(static)
        for (size_t i = 0; i < limit; ++i) {
            int32_t a = st->data[row_prev + i];
            int32_t b = st->data[row_prev + i + half];
            st->data[row_curr + i] = (a < b) ? a : b;
        }
    }
}
