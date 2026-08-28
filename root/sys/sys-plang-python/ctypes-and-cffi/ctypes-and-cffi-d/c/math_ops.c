// math_ops.c
#include <stdint.h>

int32_t add_vectors(const int32_t *a, const int32_t *b, int32_t *out, size_t n) {
    if (!a || !b || !out) return -1;
    for (size_t i = 0; i < n; ++i) {
        out[i] = a[i] + b[i];
    }
    return 0;
}
