#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

/* Безпечне множення uint64_t з перевіркою переповнення */
static bool safe_mul_u64(uint64_t a, uint64_t b, uint64_t *res) {
    if (a == 0 || b == 0) {
        *res = 0;
        return true;
    }
    if (a > UINT64_MAX / b) {
        return false; /* Сигнал про переповнення */
    }
    *res = a * b;
    return true;
}

/* Швидке цілочисельне піднесення base^exp з перевіркою переповнення */
static bool safe_pow_u64(uint64_t base, uint32_t exp, uint64_t *res) {
    uint64_t result = 1;
    uint64_t b = base;
    uint32_t e = exp;

    while (e > 0) {
        if (e & 1) {
            if (!safe_mul_u64(result, b, &result)) {
                return false;
            }
        }
        e >>= 1;
        if (e > 0) {
            if (!safe_mul_u64(b, b, &b)) {
                return false;
            }
        }
    }
    *res = result;
    return true;
}

/* Обчислення точного цілочисельного кореня b-го степеня target = y^b */
static bool exact_nth_root(uint64_t target, uint32_t b, uint64_t *root) {
    if (target == 0) { *root = 0; return true; }
    if (target == 1) { *root = 1; return true; }
    if (b == 0) return false;
    if (b == 1) { *root = target; return true; }

    uint64_t low = 1;
    uint64_t high = target;
    uint64_t ans = 0;
    bool found = false;

    /* Встановлення теоретичних верхніх меж за розрядністю uint64_t */
    if (b == 2) high = 4294967295ULL;
    else if (b == 3) high = 2642245ULL;
    else if (b == 4) high = 65535ULL;
    else if (b >= 5 && b < 64) high = 1024ULL;
    else if (b >= 64) high = 1ULL;

    while (low <= high) {
        uint64_t mid = low + (high - low) / 2;
        uint64_t p = 0;
        bool ok = safe_pow_u64(mid, b, &p);

        if (ok && p == target) {
            ans = mid;
            found = true;
            break;
        }
        if (!ok || p > target) {
            if (mid == 0) break;
            high = mid - 1;
        } else {
            low = mid + 1;
        }
    }

    if (found) {
        *root = ans;
        return true;
    }
    return false;
}

/* Структура для збереження знайденого розв'язку */
typedef struct {
    uint64_t x;
    uint64_t y;
    uint32_t a;
    uint32_t b;
} gerono_solution_t;

/* Пошук розв'язків x² - yᵇ = 1 у заданому діапазоні */
size_t scan_gerono_quad_base(uint64_t max_x, uint32_t max_b, gerono_solution_t *out_sols, size_t max_sols) {
    size_t count = 0;
    for (uint64_t x = 2; x <= max_x; ++x) {
        uint64_t target = x * x - 1;
        for (uint32_t b = 2; b <= max_b; ++b) {
            uint64_t y = 0;
            if (exact_nth_root(target, b, &y)) {
                if (count < max_sols) {
                    out_sols[count].x = x;
                    out_sols[count].y = y;
                    out_sols[count].a = 2;
                    out_sols[count].b = b;
                    count++;
                }
            }
        }
    }
    return count;
}

int main(void) {
    printf("=== Чисельний пошук розв'язків x² - yᵇ = 1 (C) ===\n");
    uint64_t max_x = 100000;
    uint32_t max_b = 10;
    
    gerono_solution_t sols[10];
    size_t n = scan_gerono_quad_base(max_x, max_b, sols, 10);

    printf("Знайдено розв'язків у діапазоні x <= %llu, b <= %u: %zu\n",
           (unsigned long long)max_x, max_b, n);

    for (size_t i = 0; i < n; ++i) {
        printf("Розв'язок #%zu: %llu^%u - %llu^%u = 1\n",
               i + 1,
               (unsigned long long)sols[i].x, sols[i].a,
               (unsigned long long)sols[i].y, sols[i].b);
    }

    return 0;
}
