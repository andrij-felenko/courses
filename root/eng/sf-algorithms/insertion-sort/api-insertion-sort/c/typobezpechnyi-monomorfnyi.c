#include <stddef.h>

#define DEFINE_INSERTION_SORT(NAME, TYPE, LESS_THAN)                         \
static inline void insertion_sort_##NAME(TYPE *arr, size_t n) {              \
    if (arr == NULL || n <= 1) return;                                       \
    for (size_t i = 1; i < n; ++i) {                                          \
        TYPE key = arr[i];                                                    \
        size_t j = i;                                                         \
        while (j > 0 && LESS_THAN(key, arr[j - 1])) {                         \
            arr[j] = arr[j - 1];                                              \
            --j;                                                              \
        }                                                                     \
        arr[j] = key;                                                         \
    }                                                                         \
}
