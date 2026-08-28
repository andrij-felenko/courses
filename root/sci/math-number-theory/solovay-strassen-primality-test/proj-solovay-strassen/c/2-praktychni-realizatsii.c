#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>

/* Безпечне модульне множення (a * b) % mod із розширенням до 128 біт */
static uint64_t mul_mod(uint64_t a, uint64_t b, uint64_t mod) {
    return (uint64_t)(((unsigned __int128)a * b) % mod);
}

/* Швидке піднесення до степеня (base^exp) % mod методом Square-and-Multiply.
   Часова складність: O(log exp) операцій множення. */
static uint64_t power_mod(uint64_t base, uint64_t exp, uint64_t mod) {
    uint64_t result = 1;
    base %= mod;
    while (exp > 0) {
        if (exp & 1) {
            result = mul_mod(result, base, mod);
        }
        base = mul_mod(base, base, mod);
        exp >>= 1;
    }
    return result;
}

/* Бінарний алгоритм найменшого спільного дільника (НСД) */
static uint64_t gcd64(uint64_t a, uint64_t b) {
    while (b != 0) {
        uint64_t temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}

/* Ітеративне обчислення символу Якобі (a / n) за квадратичним законом взаємності.
   Приймає 64-бітні знакові цілі числа. Повертає 1, -1 або 0. */
static int jacobi_symbol(int64_t a, int64_t n) {
    if (n <= 0 || (n % 2 == 0)) {
        return 0; /* Перевірка коректності: n має бути додатним і непарним */
    }

    a = (a % n + n) % n;
    int result = 1;

    while (a != 0) {
        /* Виділення степенів двійки з чисельника a */
        while (a % 2 == 0) {
            a /= 2;
            int64_t n_mod8 = n % 8;
            /* Властивість: (2 / n) = -1 якщо n ≡ 3 або 5 (mod 8) */
            if (n_mod8 == 3 || n_mod8 == 5) {
                result = -result;
            }
        }

        /* Застосування закону квадратичної взаємності:
           (a / n) = -(n / a), якщо і a, і n ≡ 3 (mod 4) */
        int64_t temp = a;
        a = n;
        n = temp;

        if (a % 4 == 3 && n % 4 == 3) {
            result = -result;
        }

        a %= n;
    }

    if (n == 1) {
        return result;
    }
    return 0; /* Якщо n > 1, то НСД(a, n) > 1, символ Якобі дорівнює 0 */
}

/* 64-бітний генератор випадкових чисел у діапазоні [min_val, max_val]
   без системного зсуву (rejection sampling) */
static uint64_t random_uint64_range(uint64_t min_val, uint64_t max_val) {
    uint64_t range = max_val - min_val + 1;
    uint64_t rand_val;
    uint64_t limit = UINT64_MAX - (UINT64_MAX % range);
    
    do {
        /* Конкатенація кількох викликів rand() для покриття 64 бітів */
        rand_val = ((uint64_t)rand() << 48) ^
                   ((uint64_t)rand() << 32) ^
                   ((uint64_t)rand() << 16) ^
                    (uint64_t)rand();
    } while (rand_val >= limit);

    return min_val + (rand_val % range);
}

/* Головна функція тесту Соловея–Штрассена.
   n — число для перевірки, k — кількість незалежних раундів. */
bool solovay_strassen_test(uint64_t n, int k) {
    if (n < 2) return false;
    if (n == 2 || n == 3) return true;
    if (n % 2 == 0) return false;

    for (int i = 0; i < k; ++i) {
        uint64_t a = random_uint64_range(2, n - 1);

        /* Перевірка наявності дільника через НСД */
        if (gcd64(a, n) > 1) {
            return false;
        }

        /* Обчислення лівої частини конгруентності: x = a^((n-1)/2) mod n */
        uint64_t x = power_mod(a, (n - 1) / 2, n);

        /* Обчислення правої частини конгруентності: символ Якобі (a / n) mod n */
        int jac = jacobi_symbol((int64_t)a, (int64_t)n);
        uint64_t jac_mod = (uint64_t)((jac % (int64_t)n + n) % n);

        /* Перевірка конгруентності Ейлера */
        if (x != jac_mod) {
            return false; /* Знайдено свідка Ейлера — число n точно складене */
        }
    }

    return true; /* Число пройшло k раундів — ймовірно просте */
}

int main(void) {
    srand((unsigned int)time(NULL));

    uint64_t candidates[] = {
        561, 1105, 1729, 2821, 6601, 8911, 10007, 10009, 104729, 65537
    };
    int num_candidates = sizeof(candidates) / sizeof(candidates[0]);

    printf("=== Демонстрація тесту Соловея–Штрассена (C) ===\n");
    for (int i = 0; i < num_candidates; ++i) {
        uint64_t n = candidates[i];
        bool is_prime = solovay_strassen_test(n, 25);
        printf("Число %8lu : %s\n", n, is_prime ? "ЙМОВІРНО ПРОСТЕ" : "СКЛАДЕНЕ");
    }

    return 0;
}
