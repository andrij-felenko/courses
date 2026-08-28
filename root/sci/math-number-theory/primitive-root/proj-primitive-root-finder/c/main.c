#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

/* Обчислення (base^exp) % mod із захистом від переповнення 64-бітних чисел */
static uint64_t power_mod(uint64_t base, uint64_t exp, uint64_t mod) {
    uint64_t result = 1;
    base %= mod;
    while (exp > 0) {
        if (exp & 1) {
            result = (uint64_t)((__uint128_t)result * base % mod);
        }
        base = (uint64_t)((__uint128_t)base * base % mod);
        exp >>= 1;
    }
    return result;
}

/* Найбільший спільний дільник (алгоритм Евкліда) */
static uint64_t gcd(uint64_t a, uint64_t b) {
    while (b != 0) {
        uint64_t temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}

/* Обчислення функції Ейлера φ(n) */
static uint64_t euler_phi(uint64_t n) {
    uint64_t result = n;
    uint64_t p = 2;
    while (p * p <= n) {
        if (n % p == 0) {
            while (n % p == 0) {
                n /= p;
            }
            result -= result / p;
        }
        p++;
    }
    if (n > 1) {
        result -= result / n;
    }
    return result;
}

/* Отримання списку унікальних простих множників числа n */
static size_t get_prime_factors(uint64_t n, uint64_t factors[], size_t max_factors) {
    size_t count = 0;
    uint64_t p = 2;
    while (p * p <= n) {
        if (n % p == 0) {
            if (count < max_factors) {
                factors[count++] = p;
            }
            while (n % p == 0) {
                n /= p;
            }
        }
        p++;
    }
    if (n > 1 && count < max_factors) {
        factors[count++] = n;
    }
    return count;
}

/* Перевірка, чи існує первісний корінь за модулем n (Критерій Ґаусса) */
static bool has_primitive_root(uint64_t n) {
    if (n == 2 || n == 4) return true;
    if (n % 2 == 0) n /= 2;
    if (n % 2 == 0) return false; /* 4 | n, але n > 4 */

    /* Перевірка, чи є n степенем простого числа p^k */
    uint64_t p = 3;
    while (p * p <= n) {
        if (n % p == 0) {
            while (n % p == 0) n /= p;
            return (n == 1); /* Лише один простий множник */
        }
        p += 2;
    }
    return true; /* n сам є простим числом */
}

/* Пошук найменшого первісного кореня за модулем n.
   Повертає 0, якщо первісного кореня не існує. */
uint64_t find_primitive_root_c(uint64_t n) {
    if (!has_primitive_root(n)) {
        return 0;
    }
    if (n == 2) return 1;

    uint64_t phi = euler_phi(n);
    uint64_t factors[64];
    size_t factor_count = get_prime_factors(phi, factors, 64);

    for (uint64_t g = 2; g < n; ++g) {
        if (gcd(g, n) != 1) continue;

        bool is_primitive = true;
        for (size_t i = 0; i < factor_count; ++i) {
            if (power_mod(g, phi / factors[i], n) == 1) {
                is_primitive = false;
                break;
            }
        }
        if (is_primitive) {
            return g;
        }
    }
    return 0;
}

int main(void) {
    uint64_t test_moduli[] = {7, 9, 14, 15, 17, 25, 31, 81};
    size_t count = sizeof(test_moduli) / sizeof(test_moduli[0]);

    for (size_t i = 0; i < count; ++i) {
        uint64_t n = test_moduli[i];
        uint64_t root = find_primitive_root_c(n);
        if (root != 0) {
            printf("Модуль %2lu: найменший первісний корінь = %lu\n", n, root);
        } else {
            printf("Модуль %2lu: первісного кореня НЕ ІСНУЄ\n", n);
        }
    }
    return 0;
}
