/* c */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>

/* Безпечне модульне множення (a * b) % mod проти переповнення uint64_t */
static uint64_t mul_mod(uint64_t a, uint64_t b, uint64_t mod) {
#if defined(__SIZEOF_INT128__)
    return (uint64_t)(((unsigned __int128)a * b) % mod);
#else
    uint64_t res = 0;
    a %= mod;
    while (b > 0) {
        if (b & 1) res = (res + a) % mod;
        a = (a * 2) % mod;
        b >>= 1;
    }
    return res;
#endif
}

/* Модульне піднесення до степеня: (base^exp) % mod */
static uint64_t power_mod(uint64_t base, uint64_t exp, uint64_t mod) {
    uint64_t res = 1;
    base %= mod;
    while (exp > 0) {
        if (exp & 1) res = mul_mod(res, base, mod);
        base = mul_mod(base, base, mod);
        exp >>= 1;
    }
    return res;
}

/* Один раунд тесту Міллера — Рабіна для основи a */
static bool miller_rabin_test_single(uint64_t n, uint64_t a, uint64_t d, int s) {
    uint64_t x = power_mod(a, d, n);
    if (x == 1 || x == n - 1) {
        return true;
    }
    for (int r = 1; r < s; ++r) {
        x = mul_mod(x, x, n);
        if (x == n - 1) {
            return true;
        }
        if (x == 1) {
            return false;
        }
    }
    return false;
}

/* Основна функція тесту простоти: k — кількість раундів (BPP-параметр) */
bool is_prime_miller_rabin(uint64_t n, int k) {
    if (n < 2) return false;
    if (n == 2 || n == 3) return true;
    if (n % 2 == 0) return false;

    /* Розклад n - 1 = 2^s * d */
    uint64_t d = n - 1;
    int s = 0;
    while ((d & 1) == 0) {
        d >>= 1;
        s++;
    }

    /* k незалежних випробувань випадкових основ */
    for (int i = 0; i < k; ++i) {
        uint64_t a = 2 + (uint64_t)rand() % (n - 3);
        if (!miller_rabin_test_single(n, a, d, s)) {
            return false; /* Гарантовано складене */
        }
    }
    return true; /* Просте з імовірністю помилки <= (1/4)^k */
}

int main(void) {
    srand((unsigned int)time(NULL));
    uint64_t candidate = 1000000007ULL;
    int rounds = 20; /* Помилка <= (1/4)^20 ≈ 10^-12 */

    if (is_prime_miller_rabin(candidate, rounds)) {
        printf("Число %llu є простим з високою ймовірністю.\n", (unsigned long long)candidate);
    } else {
        printf("Число %llu є складеним.\n", (unsigned long long)candidate);
    }
    return 0;
}
