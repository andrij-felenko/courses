#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

// Точний розрахунок індексу Жаккара для двох відсортованих масивів C
double jaccard_exact_sorted(const uint64_t *a, size_t len_a,
                            const uint64_t *b, size_t len_b) {
    if (len_a == 0 && len_b == 0) return 1.0;
    if (len_a == 0 || len_b == 0) return 0.0;

    size_t i = 0, j = 0;
    size_t intersection_cnt = 0;

    while (i < len_a && j < len_b) {
        if (a[i] == b[j]) {
            intersection_cnt++;
            i++;
            j++;
        } else if (a[i] < b[j]) {
            i++;
        } else {
            j++;
        }
    }

    size_t union_cnt = len_a + len_b - intersection_cnt;
    return (double)intersection_cnt / (double)union_cnt;
}
