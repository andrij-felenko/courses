#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Точний швидкий цілочисельний квадратний корінь для 64-бітових чисел.
   Обчислює floor(sqrt(n)) суто на цілочисельних регістрах ALU без FPU. */
static inline uint64_t isqrt64_fast(uint64_t n) {
    if (n == 0) return 0;

    uint64_t root = 0;
    /* Стартуємо з найбільшого парного степеня двійки для 64-бітового числа: 2^62 */
    uint64_t bit = (uint64_t)1 << 62;

    /* Пропускаємо провідні нулі для прискорення */
    while (bit > n) {
        bit >>= 2;
    }

    while (bit != 0) {
        if (n >= root + bit) {
            n -= root + bit;
            root = (root >> 1) + bit;
        } else {
            root >>= 1;
        }
        bit >>= 2;
    }

    return root;
}
