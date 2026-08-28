#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>

/* Таблиця перших малих простих чисел для швидкого адитивного решета */
static const uint64_t SMALL_PRIMES[] = {
    3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97
};
static const size_t NUM_SMALL_PRIMES = sizeof(SMALL_PRIMES) / sizeof(SMALL_PRIMES[0]);

/* Швидке модульне піднесення до степеня: (base^exp) % mod з захистом від переповнення 64-біт */
uint64_t mod_pow(uint64_t base, uint64_t exp, uint64_t mod) {
    uint64_t result = 1;
    base %= mod;
    while (exp > 0) {
        if (exp & 1) {
            result = (uint64_t)((__int128)result * base % mod);
        }
        base = (uint64_t)((__int128)base * base % mod);
        exp >>= 1;
    }
    return result;
}

/* Імовірнісний тест простоти Міллера — Рабіна для одного числа n з k раундами */
bool miller_rabin_test(uint64_t n, int rounds) {
    if (n < 2) return false;
    if (n == 2 || n == 3) return true;
    if (n % 2 == 0) return false;

    /* Подання n - 1 у вигляді 2^s * d */
    uint64_t d = n - 1;
    int s = 0;
    while ((d & 1) == 0) {
        d >>= 1;
        s++;
    }

    for (int i = 0; i < rounds; i++) {
        uint64_t a = 2 + rand() % (n - 3);
        uint64_t x = mod_pow(a, d, n);

        if (x == 1 || x == n - 1) continue;

        bool composite = true;
        for (int r = 1; r < s; r++) {
            x = (uint64_t)((__int128)x * x % n);
            if (x == n - 1) {
                composite = false;
                break;
            }
        }
        if (composite) return false;
    }
    return true;
}

/* Стадія 1: Перевірка кандидату на подільність малими простими числами */
bool passes_sieve(uint64_t n) {
    for (size_t i = 0; i < NUM_SMALL_PRIMES; i++) {
        if (n == SMALL_PRIMES[i]) return true;
        if (n % SMALL_PRIMES[i] == 0) return false;
    }
    return true;
}

/* Стадія 2: Двостадійний генератор безпечного простого числа q = 2p + 1 */
bool generate_safe_prime_c(uint64_t min_val, uint64_t max_val, uint64_t *out_p, uint64_t *out_q) {
    for (uint64_t p = min_val; p <= max_val; p++) {
        /* Примусове модулярне затискання: перевіряємо лише p = 6k + 5 */
        if (p % 6 != 5) continue;

        uint64_t q = 2 * p + 1;

        /* Первинне решето відсіює понад 85% складених чисел */
        if (!passes_sieve(p) || !passes_sieve(q)) continue;

        /* Парний тест Міллера — Рабіна: спочатку p, потім q */
        if (miller_rabin_test(p, 25) && miller_rabin_test(q, 25)) {
            *out_p = p;
            *out_q = q;
            return true;
        }
    }
    return false;
}

int main(void) {
    srand((unsigned int)time(NULL));
    uint64_t p = 0, q = 0;
    printf("=== Генерація безпечних простих чисел (Стандарт C) ===\n");
    if (generate_safe_prime_c(1000000, 2000000, &p, &q)) {
        printf("Знайдено просте Софі Жермен p = %llu\n", (unsigned long long)p);
        printf("Знайдено безпечне просте q = 2p + 1 = %llu\n", (unsigned long long)q);
        printf("Перевірка затискання p %% 6 = %llu (очікується 5)\n", (unsigned long long)(p % 6));
    } else {
        printf("Безпечних простих чисел у заданому діапазоні не знайдено.\n");
    }
    return 0;
}
