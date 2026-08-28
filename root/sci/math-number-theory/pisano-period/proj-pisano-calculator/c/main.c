#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>

/* Структура 2x2 матриці для модулярної арифметики */
typedef struct {
    uint64_t m[2][2];
} Matrix2x2;

/* Бепечне 64-бітне множення за модулем mod із захистом від переповнення */
static inline uint64_t safe_mul_mod(uint64_t a, uint64_t b, uint64_t mod) {
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

/* Множення двох матриць 2x2 за модулем mod */
static Matrix2x2 mat_mul(Matrix2x2 A, Matrix2x2 B, uint64_t mod) {
    Matrix2x2 C;
    for (int i = 0; i < 2; ++i) {
        for (int j = 0; j < 2; ++j) {
            uint64_t sum = 0;
            for (int k = 0; k < 2; ++k) {
                uint64_t prod = safe_mul_mod(A.m[i][k], B.m[k][j], mod);
                sum = (sum + prod) % mod;
            }
            C.m[i][j] = sum;
        }
    }
    return C;
}

/* Швидке бінарне піднесення матриці Q до степеня n за модулем mod */
static Matrix2x2 mat_pow(Matrix2x2 Q, uint64_t n, uint64_t mod) {
    Matrix2x2 res = {{{1, 0}, {0, 1}}}; /* Одинична матриця */
    Matrix2x2 base = Q;
    while (n > 0) {
        if (n & 1) {
            res = mat_mul(res, base, mod);
        }
        base = mat_mul(base, base, mod);
        n >>= 1;
    }
    return res;
}

/* Обчислення n-го числа Фібоначчі за модулем mod за O(log n) */
uint64_t fibonacci_mod(uint64_t n, uint64_t mod) {
    if (n == 0 || mod == 1) return 0;
    Matrix2x2 Q = {{{1, 1}, {1, 0}}};
    Matrix2x2 R = mat_pow(Q, n - 1, mod);
    return R.m[0][0];
}

/* Обчислення НСД (найбільшого спільного дільника) */
static uint64_t gcd64(uint64_t a, uint64_t b) {
    while (b != 0) {
        uint64_t t = b;
        b = a % b;
        a = t;
    }
    return a;
}

/* Обчислення НСК (найменшого спільного кратного) */
static uint64_t lcm64(uint64_t a, uint64_t b) {
    if (a == 0 || b == 0) return 0;
    return (a / gcd64(a, b)) * b;
}

/* Пошук періоду Пізано π(m) методом лінійної ітерації */
uint64_t pisano_period_linear(uint64_t m) {
    if (m <= 1) return 1;

    uint64_t prev = 0;
    uint64_t curr = 1;
    uint64_t max_steps = m * 6; /* Оцінка верхньої межі 6m */

    for (uint64_t i = 0; i < max_steps; ++i) {
        uint64_t next = (prev + curr) % m;
        prev = curr;
        curr = next;

        /* Умова повернення до початкового стану (0, 1) */
        if (prev == 0 && curr == 1) {
            return i + 1;
        }
    }
    return 0;
}

int main(void) {
    uint64_t m = 1000;
    uint64_t period = pisano_period_linear(m);
    printf("Pisano period pi(%llu) = %llu\n", (unsigned long long)m, (unsigned long long)period);

    uint64_t n = 1000000000000000000ULL; /* 10^18 */
    uint64_t n_reduced = n % period;
    uint64_t fn = fibonacci_mod(n_reduced, m);

    printf("F(10^18) mod %llu = %llu\n", (unsigned long long)m, (unsigned long long)fn);
    return 0;
}
