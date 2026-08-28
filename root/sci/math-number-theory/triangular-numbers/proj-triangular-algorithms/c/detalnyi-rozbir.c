#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

/* Обчислення точного цілочисельного квадратного кореня за методом Ньютона */
static uint64_t integer_sqrt(uint64_t n) {
    if (n == 0) return 0;
    
    uint64_t x = n;
    uint64_t y = (x + 1) / 2;
    while (y < x) {
        x = y;
        y = (x + n / x) / 2;
    }
    return x;
}

/* Перевірка, чи є число M трикутним */
bool is_triangular(uint64_t m, uint64_t *out_n) {
    if (m == 0) {
        if (out_n) *out_n = 0;
        return true;
    }
    
    /* Фільтрація переповнення 64-бітного цілого (8M + 1 <= UINT64_MAX) */
    if (m > (UINT64_MAX - 1) / 8) {
        return false;
    }
    
    /* Швидкий фільтр за цифровим коренем (модуль 9) */
    uint64_t rem9 = m % 9;
    if (rem9 == 2 || rem9 == 4 || rem9 == 5 || rem9 == 7 || rem9 == 8) {
        return false;
    }
    
    uint64_t disc = 8 * m + 1;
    uint64_t s = integer_sqrt(disc);
    
    /* Перевіряємо, чи є дискримінант точним квадратом */
    if (s * s != disc) {
        return false;
    }
    
    /* Дискримінант 8M + 1 для ненульового M завжди непарний */
    if ((s & 1) == 0) {
        return false;
    }
    
    if (out_n) {
        *out_n = (s - 1) / 2;
    }
    return true;
}
