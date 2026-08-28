#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <omp.h>

// Модулярне множення (a * b) % mod з підтримкою __int128
static inline uint64_t mul_mod_c(uint64_t a, uint64_t b, uint64_t mod) {
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

// Модулярне піднесення до степеня
static uint64_t power_mod_c(uint64_t base, uint64_t exp, uint64_t mod) {
    uint64_t res = 1;
    base %= mod;
    while (exp > 0) {
        if (exp & 1) res = mul_mod_c(res, base, mod);
        base = mul_mod_c(base, base, mod);
        exp >>= 1;
    }
    return res;
}

// Перевірка простоти Міллера — Рабіна (C11)
static bool is_prime_mr(uint64_t n) {
    if (n < 2) return false;
    if (n == 2 || n == 3) return true;
    if (n % 2 == 0 || n % 3 == 0) return false;

    uint64_t d = n - 1;
    int s = 0;
    while (d % 2 == 0) {
        d /= 2;
        s++;
    }

    static const uint64_t bases[] = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37};
    int num_bases = sizeof(bases) / sizeof(bases[0]);

    for (int i = 0; i < num_bases; ++i) {
        uint64_t a = bases[i];
        if (n <= a) break;

        uint64_t x = power_mod_c(a, d, n);
        if (x == 1 || x == n - 1) continue;

        bool composite = true;
        for (int r = 1; r < s; ++r) {
            x = mul_mod_c(x, x, n);
            if (x == n - 1) {
                composite = false;
                break;
            }
        }
        if (composite) return false;
    }
    return true;
}

// Перевірка довжини ланцюжка
static int get_chain_length_c(uint64_t p1) {
    int length = 0;
    uint64_t current = p1;

    while (is_prime_mr(current)) {
        length++;
        if (current > (UINT64_MAX - 1) / 2) break;
        current = 2 * current + 1;
    }
    return length;
}

// Паралельний пошук ланцюжків (C11 + OpenMP)
void search_chains_c(uint64_t start_val, uint64_t end_val, int target_k) {
    printf("[C] Пошук ланцюжків 1-го роду довжини k >= %d у діапазоні [%llu, %llu]...\n",
           target_k, (unsigned long long)start_val, (unsigned long long)end_val);

    uint64_t step = 2310;
    int64_t first_m = (int64_t)((start_val + step) / step);
    int64_t last_m  = (int64_t)(end_val / step);

    #pragma omp parallel for schedule(dynamic, 1000)
    for (int64_t m = first_m; m <= last_m; ++m) {
        uint64_t p1 = (uint64_t)m * step - 1;
        if (p1 < start_val || p1 > end_val) continue;

        int len = get_chain_length_c(p1);
        if (len >= target_k) {
            #pragma omp critical
            {
                printf("Знайдено ланцюжок довжини k = %d! Стартове p1 = %llu\n",
                       len, (unsigned long long)p1);
                uint64_t curr = p1;
                for (int i = 1; i <= len; ++i) {
                    printf("  p_%d = %llu\n", i, (unsigned long long)curr);
                    curr = 2 * curr + 1;
                }
            }
        }
    }
}

int main(void) {
    uint64_t start = 1000000ULL;
    uint64_t end   = 50000000ULL;
    int target_k  = 5;

    double t0 = omp_get_wtime();
    search_chains_c(start, end, target_k);
    double t1 = omp_get_wtime();

    printf("Обчислення завершено за %.4f секунд.\n", t1 - t0);
    return 0;
}
