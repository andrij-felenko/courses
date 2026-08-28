#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>

#define MAX_DEG 32

typedef struct {
    int64_t coeffs[MAX_DEG];
    int deg;
} Poly;

int poly_deg(const Poly* p) {
    for (int i = p->deg; i >= 0; --i) {
        if (p->coeffs[i] != 0) return i;
    }
    return -1;
}

void poly_normalize(Poly* p) {
    p->deg = poly_deg(p);
    if (p->deg < 0) {
        p->deg = 0;
        p->coeffs[0] = 0;
    }
}

double poly_norm_l2(const Poly* p) {
    double sum = 0.0;
    for (int i = 0; i <= p->deg; ++i) {
        sum += (double)(p->coeffs[i] * p->coeffs[i]);
    }
    return sqrt(sum);
}

int64_t n_choose_k(int n, int k) {
    if (k < 0 || k > n) return 0;
    if (k == 0 || k == n) return 1;
    if (k > n / 2) k = n - k;
    int64_t res = 1;
    for (int i = 1; i <= k; ++i) {
        res = res * (n - i + 1) / i;
    }
    return res;
}

int64_t mignotte_bound(const Poly* p) {
    int n = poly_deg(p);
    if (n <= 1) return 0;
    int64_t comb = n_choose_k(n, n / 2);
    double l2 = poly_norm_l2(p);
    return (int64_t)ceil(comb * l2);
}

void symmetric_mod(const Poly* src, Poly* dst, int64_t m) {
    int64_t half = m / 2;
    dst->deg = src->deg;
    for (int i = 0; i <= src->deg; ++i) {
        int64_t rem = src->coeffs[i] % m;
        if (rem < 0) rem += m;
        if (rem > half) rem -= m;
        dst->coeffs[i] = rem;
    }
    poly_normalize(dst);
}

int main(void) {
    Poly f;
    f.deg = 6;
    f.coeffs[0] = -12; f.coeffs[1] = 8; f.coeffs[2] = -8;
    f.coeffs[3] = 1;   f.coeffs[4] = 2; f.coeffs[5] = -1;
    f.coeffs[6] = 1;

    int64_t bound = mignotte_bound(&f);
    printf("Евклідова норма ||f||_2: %.4f\n", poly_norm_l2(&f));
    printf("Межа Міньотта B(f): %lld\n", (long long)bound);
    printf("Критерій зупинки: p^k > %lld\n", (long long)(2 * bound));

    Poly g_lifted;
    g_lifted.deg = 3;
    g_lifted.coeffs[0] = 122; g_lifted.coeffs[1] = 2;
    g_lifted.coeffs[2] = 0;   g_lifted.coeffs[3] = 1;

    Poly g_final;
    symmetric_mod(&g_lifted, &g_final, 625);

    printf("Відновлені коефіцієнти g(x): ");
    for (int i = 0; i <= g_final.deg; ++i) {
        printf("%lld ", (long long)g_final.coeffs[i]);
    }
    printf("\n");

    return 0;
}
