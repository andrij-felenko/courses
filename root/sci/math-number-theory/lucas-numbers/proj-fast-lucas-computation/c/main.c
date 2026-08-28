#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

/* Структура для збереження пари сусідніх чисел Люка (Lₖ, Lₖ₊₁) */
typedef struct {
    uint64_t l_k;
    uint64_t l_k1;
} lucas_pair_t;

/* 
 * Обчислює пару (Lₙ, Lₙ₊₁) за час O(log n)
 * Використовує 64-бітну цілочисельну арифметику без переповнення для n <= 92
 */
lucas_pair_t fast_lucas_pair(uint32_t n) {
    if (n == 0) {
        lucas_pair_t base = {2, 1};
        return base;
    }

    /* Знаходимо позицію старшого встановленого біта */
    uint32_t mask = 1U << 31;
    while ((mask & n) == 0) {
        mask >>= 1;
    }

    uint64_t a = 2; /* L₀ */
    uint64_t b = 1; /* L₁ */
    uint32_t k = 0;

    while (mask > 0) {
        /* Формули подвоєння: k -> 2k */
        int sign = (k % 2 == 0) ? 1 : -1;
        uint64_t next_a = a * a - (uint64_t)(2 * sign);
        uint64_t next_b = a * b - (uint64_t)sign;

        a = next_a;
        b = next_b;
        k = 2 * k;

        /* Якщо поточний біт дорівнює 1: 2k -> 2k + 1 */
        if ((n & mask) != 0) {
            uint64_t temp = a + b;
            a = b;
            b = temp;
            k = k + 1;
        }

        mask >>= 1;
    }

    lucas_pair_t res = {a, b};
    return res;
}

uint64_t fast_lucas(uint32_t n) {
    return fast_lucas_pair(n).l_k;
}

/*
 * Тест Люка-Лемера для перевірки простоти числа Мерсенна M_p = 2^p - 1
 */
bool lucas_lehmer_test(uint32_t p) {
    if (p == 2) return true;
    uint64_t m_p = (1ULL << p) - 1ULL;
    uint64_t s = 4;
    for (uint32_t i = 0; i < p - 2; ++i) {
        s = (s * s - 2) % m_p;
    }
    return s == 0;
}

int main(void) {
    printf("Обчислення чисел Люка (C):\n");
    for (uint32_t n = 0; n <= 15; ++n) {
        printf("L_%-2u = %llu\n", n, (unsigned long long)fast_lucas(n));
    }
    printf("\nПеревірка чисел Мерсенна M_p:\n");
    uint32_t primes[] = {3, 5, 7, 13, 17, 19, 31};
    for (size_t i = 0; i < sizeof(primes)/sizeof(primes[0]); ++i) {
        uint32_t p = primes[i];
        printf("M_%-2u є %s\n", p, lucas_lehmer_test(p) ? "ПРОСТИМ" : "СКЛАДЕНИМ");
    }
    return 0;
}
