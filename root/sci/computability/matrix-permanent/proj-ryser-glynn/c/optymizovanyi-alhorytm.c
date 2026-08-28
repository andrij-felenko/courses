#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

/* Обчислення перманента за формулою Райзера з кодом Ґрея */
uint64_t permanent_ryser_u64(const uint64_t *matrix, size_t n) {
    if (!matrix || n == 0 || n > 62) return 0;

    uint64_t *row_sum = (uint64_t *)calloc(n, sizeof(uint64_t));
    if (!row_sum) return 0;

    uint64_t total_sum = 0;
    uint64_t num_subsets = 1ULL << n;
    uint64_t prev_gray = 0;

    for (uint64_t i = 1; i < num_subsets; ++i) {
        uint64_t gray = i ^ (i >> 1);
        uint64_t diff = gray ^ prev_gray;

        /* Знаходимо номер зміненого біта за допомогою builtin_ctzll */
        size_t bit_idx = (size_t)__builtin_ctzll(diff);
        bool is_added = (gray & diff) != 0;

        /* Інкрементне оновлення сум рядків */
        if (is_added) {
            for (size_t r = 0; r < n; ++r) {
                row_sum[r] += matrix[r * n + bit_idx];
            }
        } else {
            for (size_t r = 0; r < n; ++r) {
                row_sum[r] -= matrix[r * n + bit_idx];
            }
        }

        /* Обчислення добутку рядкових сум */
        uint64_t prod = 1;
        for (size_t r = 0; r < n; ++r) {
            prod *= row_sum[r];
        }

        /* Ураховуємо знак (-1)|S| в залежності від парності ваги Геммінга */
        size_t subset_size = (size_t)__builtin_popcountll(gray);
        if (subset_size & 1) {
            total_sum -= prod;
        } else {
            total_sum += prod;
        }

        prev_gray = gray;
    }

    free(row_sum);

    /* Якщо n непарне, домножуємо на (-1)ⁿ */
    if (n & 1) {
        total_sum = (uint64_t)(-(int64_t)total_sum);
    }

    return total_sum;
}
