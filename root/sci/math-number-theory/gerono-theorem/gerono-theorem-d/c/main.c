#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

/* Безпечне множення з перевіркою переповнення uint64_t */
static bool safe_mul(uint64_t a, uint64_t b, uint64_t *res) {
    if (a == 0 || b == 0) { *res = 0; return true; }
    if (a > UINT64_MAX / b) return false;
    *res = a * b;
    return true;
}

/* Швидке піднесення base^exp з перевіркою переповнення */
static bool safe_pow(uint64_t base, uint32_t exp, uint64_t *res) {
    uint64_t r = 1, b = base;
    while (exp > 0) {
        if (exp & 1) {
            if (!safe_mul(r, b, &r)) return false;
        }
        exp >>= 1;
        if (exp > 0) {
            if (!safe_mul(b, b, &b)) return false;
        }
    }
    *res = r;
    return true;
}

/* Перевірка рівняння x² - yᵇ = 1 у діапазоні */
void check_gerono_c(uint64_t max_x, uint32_t max_b) {
    for (uint64_t x = 2; x <= max_x; ++x) {
        uint64_t target = x * x - 1;
        for (uint32_t b = 2; b <= max_b; ++b) {
            uint64_t low = 1, high = target, y_ans = 0;
            if (b == 2) high = 4294967295ULL;
            else if (b == 3) high = 2642245ULL;
            else if (b >= 4) high = 65535ULL;

            while (low <= high) {
                uint64_t mid = low + (high - low) / 2;
                uint64_t p = 0;
                bool ok = safe_pow(mid, b, &p);
                if (ok && p == target) { y_ans = mid; break; }
                if (!ok || p > target) { if (mid == 0) break; high = mid - 1; }
                else { low = mid + 1; }
            }
            if (y_ans > 0) {
                printf("Знайдено розв'язок: %llu^2 - %llu^%u = 1\n",
                       (unsigned long long)x, (unsigned long long)y_ans, b);
            }
        }
    }
}
