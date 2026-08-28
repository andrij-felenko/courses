#include <stdio.h>
#include <stdlib.h>

// Повертає 0-based індекс першого елемента, префіксна сума якого >= target_sum
size_t fenwick_lower_bound(const fenwick_tree_t* ft, long long target_sum) {
    if (!ft || target_sum <= 0) return 0;

    size_t idx = 0;
    long long current_sum = 0;

    size_t max_pow = 1;
    while ((max_pow << 1) <= ft->size) {
        max_pow <<= 1;
    }

    for (size_t len = max_pow; len > 0; len >>= 1) {
        size_t next_idx = idx + len;
        if (next_idx <= ft->size && current_sum + ft->tree[next_idx] < target_sum) {
            idx = next_idx;
            current_sum += ft->tree[idx];
        }
    }

    return idx;
}
