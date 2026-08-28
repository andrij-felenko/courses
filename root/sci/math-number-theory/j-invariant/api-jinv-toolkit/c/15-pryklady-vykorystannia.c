#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#define P_MOD 431LL

typedef struct { int64_t re, im; } fp2_t;
typedef struct { fp2_t a, b; } curve_short_t;

/* Модульні допоміжні операції */
static inline int64_t mod(int64_t x) { int64_t r = x % P_MOD; return r < 0 ? r + P_MOD : r; }
static inline fp2_t fp2_add(fp2_t x, fp2_t y) { return (fp2_t){ mod(x.re + y.re), mod(x.im + y.im) }; }
static inline fp2_t fp2_sub(fp2_t x, fp2_t y) { return (fp2_t){ mod(x.re - y.re), mod(x.im - y.im) }; }
static inline fp2_t fp2_mul(fp2_t x, fp2_t y) {
    return (fp2_t){ mod(x.re * y.re - x.im * y.im), mod(x.re * y.im + x.im * y.re) };
}
static int64_t p_pow(int64_t b, int64_t e) {
    int64_t r = 1; b = mod(b);
    while (e > 0) { if (e & 1) r = mod(r * b); b = mod(b * b); e >>= 1; }
    return r;
}
static inline fp2_t fp2_inv(fp2_t x) {
    int64_t n_inv = p_pow(mod(x.re * x.re + x.im * x.im), P_MOD - 2);
    return (fp2_t){ mod(x.re * n_inv), mod(-x.im * n_inv) };
}

/* API-функція обчислення j-інваріанта */
bool jinv_compute(curve_short_t crv, fp2_t *j_res) {
    fp2_t a3 = fp2_mul(crv.a, fp2_mul(crv.a, crv.a));
    fp2_t b2 = fp2_mul(crv.b, crv.b);
    fp2_t num = fp2_mul((fp2_t){1728, 0}, fp2_mul((fp2_t){4, 0}, a3));
    fp2_t den = fp2_add(fp2_mul((fp2_t){4, 0}, a3), fp2_mul((fp2_t){27, 0}, b2));

    if (den.re == 0 && den.im == 0) return false;
    *j_res = fp2_mul(num, fp2_inv(den));
    return true;
}

int main(void) {
    printf("=== Демонстрація C API libjinv ===\n");
    curve_short_t e1 = { {1, 0}, {0, 0} }; /* y^2 = x^3 + x */
    fp2_t j1;
    if (jinv_compute(e1, &j1)) {
        printf("Крива y^2 = x^3 + x -> j = %lld (очікується 1728 mod 431 = %lld)\n",
               (long long)j1.re, (long long)(1728 % P_MOD));
    }
    return 0;
}
