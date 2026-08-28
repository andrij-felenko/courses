#include <stdint.h>
#include <stdbool.h>

#define MAX_N 1024
#define MAX_LEVELS 11 /* 2^10 = 1024 -> 11 рівнів */

/* Статичний буфер у BSS без динамічної алокації */
static int32_t g_st_data[MAX_LEVELS][MAX_N];
static size_t g_st_size = 0;

void st_init_static(const int32_t *arr, size_t n) {
    if (n > MAX_N) n = MAX_N;
    g_st_size = n;

    for (size_t i = 0; i < n; ++i) {
        g_st_data[0][i] = arr[i];
    }

    for (size_t j = 1; (size_t)(1 << j) <= n; ++j) {
        size_t half = 1 << (j - 1);
        for (size_t i = 0; i + (1 << j) <= n; ++i) {
            int32_t a = g_st_data[j - 1][i];
            int32_t b = g_st_data[j - 1][i + half];
            g_st_data[j][i] = (a < b) ? a : b;
        }
    }
}

int32_t st_query_static(size_t l, size_t r) {
    size_t len = r - l + 1;
    size_t k = (size_t)(31 - __builtin_clz((uint32_t)len));
    size_t shift = (size_t)1 << k;

    int32_t a = g_st_data[k][l];
    int32_t b = g_st_data[k][r - shift + 1];
    return (a < b) ? a : b;
}
