/* Обчислення базових функцій обмеженої арифметики мовою C */
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

/* Обчислення бітової довжини |x| = ceil(log2(x + 1)), |0| = 0 */
uint32_t bit_length(uint64_t x) {
    if (x == 0) return 0;
    uint32_t len = 0;
    while (x > 0) {
        len++;
        x >>= 1; /* x = floor(x / 2) */
    }
    return len;
}

/* Обчислення функції smash: x # y = 2^{|x| * |y|} */
bool smash_function(uint64_t x, uint64_t y, uint64_t *result) {
    uint32_t len_x = bit_length(x);
    uint32_t len_y = bit_length(y);
    uint64_t power = (uint64_t)len_x * (uint64_t)len_y;

    if (power >= 64) {
        return false; /* Переповнення 64-бітного беззнакового типу */
    }

    *result = ((uint64_t)1) << power;
    return true;
}

/* Емуляція кроку префіксної індукції PIND для обчислення кількості одиничних бітів */
uint32_t pind_popcount(uint64_t x) {
    if (x == 0) return 0;
    
    /* Рекурсивний або стековий перехід: обчислюємо для floor(x / 2), потім для x */
    uint64_t prefixes[64];
    int depth = 0;
    
    uint64_t curr = x;
    while (curr > 0) {
        prefixes[depth++] = curr;
        curr >>= 1; /* curr = floor(curr / 2) */
    }

    /* Індуктивне розгортання: рівно |x| кроків замість x кроків */
    uint32_t witness = 0; /* База індукції: phi(0) = 0 */
    for (int i = depth - 1; i >= 0; i--) {
        uint64_t val = prefixes[i];
        witness = witness + (uint32_t)(val & 1); /* Індуктивний перехід */
    }

    return witness;
}
