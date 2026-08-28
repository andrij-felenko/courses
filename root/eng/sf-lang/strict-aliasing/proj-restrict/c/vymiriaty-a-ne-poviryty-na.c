#include <stdint.h>
#include <stddef.h>

// у файлі add_plain.c
void vec_add_plain(float* out, const float* a, const float* b, size_t n) {
    for (size_t i = 0; i < n; i++) out[i] = a[i] + b[i];
}

// у файлі add_restrict.c
void vec_add_restrict(float* restrict out,
                      const float* restrict a,
                      const float* restrict b, size_t n) {
    for (size_t i = 0; i < n; i++) out[i] = a[i] + b[i];
}
