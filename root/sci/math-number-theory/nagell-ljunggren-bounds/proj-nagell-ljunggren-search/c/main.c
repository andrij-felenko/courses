#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/* Обчислення модулярного степеня (base^exp) % mod */
static uint64_t power_mod(uint64_t base, uint64_t exp, uint64_t mod) {
    uint64_t result = 1;
    base %= mod;
    while (exp > 0) {
        if (exp & 1) {
            result = (unsigned __int128)result * base % mod;
        }
        base = (unsigned __int128)base * base % mod;
        exp >>= 1;
    }
    return result;
}

/* Обчислення реп'юніта N_n(x) mod p */
static uint64_t repunit_mod(uint64_t x, uint64_t n, uint64_t p) {
    uint64_t x_mod = x % p;
    if (x_mod == 1) {
        return n % p;
    }
    uint64_t num = (power_mod(x_mod, n, p) + p - 1) % p;
    uint64_t den = x_mod - 1;
    uint64_t den_inv = power_mod(den, p - 2, p); /* за малою теоремою Ферма */
    return (unsigned __int128)num * den_inv % p;
}

/* Перевірка, чи є val q-им лишком за модулем p */
static bool is_qth_residue_mod_p(uint64_t val, uint64_t q, uint64_t p) {
    if (val % p == 0) return true;
    uint64_t gcd_q = 1;
    uint64_t a = p - 1, b = q;
    while (b != 0) {
        uint64_t t = b;
        b = a % b;
        a = t;
    }
    gcd_q = a;
    uint64_t exp = (p - 1) / gcd_q;
    return power_mod(val, exp, p) == 1;
}

/* Швидкий модулярний фільтр за набором малих простих чисел */
static bool fast_modular_sieve(uint64_t x, uint64_t n, uint64_t q) {
    static const uint64_t primes[] = {3, 5, 7, 11, 13, 17, 19, 23, 29, 31};
    size_t num_primes = sizeof(primes) / sizeof(primes[0]);

    for (size_t i = 0; i < num_primes; ++i) {
        uint64_t p = primes[i];
        if (q % (p - 1) == 0) continue;
        uint64_t rep_mod = repunit_mod(x, n, p);
        if (!is_qth_residue_mod_p(rep_mod, q, p)) {
            return false; /* Кандидат відхилено */
        }
    }
    return true; /* Пройшов модулярне сіювання */
}

/* Перевірка 64-бітного кандидата на точний степінь */
static bool verify_candidate_64bit(uint64_t x, uint64_t n, uint64_t q, uint64_t *out_y) {
    /* Точне обчислення реп'юніта N_n(x) з контролем переповнення */
    unsigned __int128 repunit = 0;
    unsigned __int128 current_term = 1;
    for (uint64_t i = 0; i < n; ++i) {
        repunit += current_term;
        if (i + 1 < n) {
            current_term *= x;
            if (current_term > UINT64_MAX) return false; /* Переповнення 64 біт */
        }
    }

    /* Наближене вилучення кореня q-го степеня */
    double double_rep = (double)repunit;
    double y_double = pow(double_rep, 1.0 / (double)q);
    uint64_t y_candidate = (uint64_t)round(y_double);

    if (y_candidate < 2) return false;

    /* Точна перевірка піднесенням до степеня y_candidate^q */
    unsigned __int128 pow_y = 1;
    for (uint64_t i = 0; i < q; ++i) {
        pow_y *= y_candidate;
        if (pow_y > repunit) break;
    }

    if (pow_y == repunit) {
        *out_y = y_candidate;
        return true;
    }
    return false;
}

int main(void) {
    printf("Пошук розв'язків рівняння Нагеля-Люнггрена (64-бітний діапазон)...\n");

    uint64_t found_count = 0;
    for (uint64_t x = 2; x <= 100; ++x) {
        for (uint64_t n = 3; n <= 30; ++n) {
            for (uint64_t q = 2; q <= 10; ++q) {
                if (!fast_modular_sieve(x, n, q)) {
                    continue;
                }
                uint64_t y = 0;
                if (verify_candidate_64bit(x, n, q, &y)) {
                    printf("ЗНАЙДЕНО РОЗВ'ЯЗОК: x = %llu, n = %llu, y = %llu, q = %llu\n",
                           (unsigned long long)x, (unsigned long long)n,
                           (unsigned long long)y, (unsigned long long)q);
                    found_count++;
                }
            }
        }
    }
    printf("Пошук завершено. Знайдено розв'язків: %llu\n", (unsigned long long)found_count);
    return 0;
}
