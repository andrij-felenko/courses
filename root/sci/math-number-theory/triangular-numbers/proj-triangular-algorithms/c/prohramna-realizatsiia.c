#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint64_t index_n;
    uint64_t root_k;
    uint64_t value_n;
} SquareTriangularNumber;

/* Генерація перших count квадратних трикутних чисел */
size_t generate_square_triangular(SquareTriangularNumber *out_arr, size_t max_count) {
    if (max_count == 0 || out_arr == NULL) return 0;

    uint64_t n = 1;
    uint64_t k = 1;
    size_t generated = 0;

    while (generated < max_count) {
        out_arr[generated].index_n = n;
        out_arr[generated].root_k = k;
        out_arr[generated].value_n = k * k;
        generated++;

        /* Перевірка на можливе 64-бітне переповнення перед наступним кроком */
        if (n > (UINT64_MAX - 4 * k - 1) / 3) {
            break;
        }

        uint64_t next_n = 3 * n + 4 * k + 1;
        uint64_t next_k = 2 * n + 3 * k + 1;

        n = next_n;
        k = next_k;
    }

    return generated;
}
