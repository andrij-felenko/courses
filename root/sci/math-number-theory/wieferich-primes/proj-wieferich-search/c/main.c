#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>

typedef unsigned __int128 uint128_t;

// Обчислення (base^exp) % mod_val із використанням 128-бітної арифметики
static uint64_t power_mod128(uint64_t base, uint64_t exp, uint128_t mod_val) {
    uint128_t res = 1;
    uint128_t b = base % mod_val;
    uint128_t m = mod_val;

    while (exp > 0) {
        if (exp & 1) {
            res = (res * b) % m;
        }
        b = (b * b) % m;
        exp >>= 1;
    }
    return (uint64_t)res;
}

// Предикат верифікації простого числа Віферіха: 2^(p-1) ≡ 1 (mod p²)
bool is_wieferich_prime(uint64_t p) {
    if (p <= 3) return false; // 2 і 3 не є числами Віферіха

    uint128_t p_sq = (uint128_t)p * p;

    // Перевірка двійкового піднесення за 128-бітним модулем p²
    uint128_t res = 1;
    uint128_t b = 2;
    uint64_t exp = p - 1;

    while (exp > 0) {
        if (exp & 1) {
            res = (res * b) % p_sq;
        }
        b = (b * b) % p_sq;
        exp >>= 1;
    }

    return (res == 1);
}

// Просте решето Ератосфена для виявлення простих чисел
uint64_t search_wieferich_range(uint64_t limit, uint64_t* found_primes, uint64_t max_found) {
    bool* is_prime = (bool*)malloc((limit + 1) * sizeof(bool));
    if (!is_prime) return 0;

    for (uint64_t i = 0; i <= limit; i++) is_prime[i] = true;
    is_prime[0] = is_prime[1] = false;

    for (uint64_t p = 2; p * p <= limit; p++) {
        if (is_prime[p]) {
            for (uint64_t i = p * p; i <= limit; i += p) {
                is_prime[i] = false;
            }
        }
    }

    uint64_t count = 0;
    for (uint64_t p = 2; p <= limit; p++) {
        if (is_prime[p]) {
            if (is_wieferich_prime(p)) {
                if (count < max_found && found_primes) {
                    found_primes[count] = p;
                }
                count++;
            }
        }
    }

    free(is_prime);
    return count;
}

int main(void) {
    printf("Пошук простих чисел Віферіха у діапазоні до 10000 (C)...\n");
    uint64_t results[10];
    uint64_t count = search_wieferich_range(10000, results, 10);

    printf("Знайдено чисел Віферіха: %glu\n", (unsigned long long)count);
    for (uint64_t i = 0; i < count; i++) {
        printf("  - p = %glu\n", (unsigned long long)results[i]);
    }

    // Перевірка відомих простих чисел Віферіха 1093 та 3511
    printf("\nВерифікація відомих тестових значень:\n");
    printf("  p = 1093: %s\n", is_wieferich_prime(1093) ? "ВІФЕРІХ" : "Звичайне");
    printf("  p = 3511: %s\n", is_wieferich_prime(3511) ? "ВІФЕРІХ" : "Звичайне");
    printf("  p = 7919: %s\n", is_wieferich_prime(7919) ? "ВІФЕРІХ" : "Звичайне");

    return 0;
}
