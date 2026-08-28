#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

/* Обчислення чисел Белла від B_0 до B_n у буфер out_bell (розмір n + 1).
   Оптимізовано за пам'яттю до O(n).
   Повертає 0 у разі успіху, -1 у разі помилки виділення пам'яті, -2 якщо n > 25 */
int compute_bell_numbers(size_t n, uint64_t *out_bell) {
    if (!out_bell) return -1;
    if (n > 25) {
        /* B_26 перевищує межу 64-бітного цілого uint64_t */
        return -2;
    }

    uint64_t *row = (uint64_t *)malloc((n + 1) * sizeof(uint64_t));
    if (!row) return -1;

    row[0] = 1;
    out_bell[0] = 1;

    for (size_t i = 1; i <= n; ++i) {
        /* Перший елемент нового рядка дорівнює останньому елементу попереднього */
        uint64_t prev = row[0];
        row[0] = row[i - 1];
        out_bell[i] = row[0];

        for (size_t j = 1; j <= i; ++j) {
            uint64_t temp = row[j];
            row[j] = row[j - 1] + prev;
            prev = temp;
        }
    }

    free(row);
    return 0;
}

int main(void) {
    const size_t N = 15;
    uint64_t bell[16];

    if (compute_bell_numbers(N, bell) == 0) {
        printf("Перші 16 чисел Белла:\n");
        for (size_t i = 0; i <= N; ++i) {
            printf("B_%-2zu = %llu\n", i, (unsigned long long)bell[i]);
        }
    }
    return 0;
}
