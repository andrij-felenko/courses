#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

/* Базове просте число: p = 431 (p ≡ 3 mod 4, надсингулярний граф Pizer) */
#define P_PRIME 431LL

/* Структура елемента квадратичного розширення F_{p^2} = F_p[i] / (i^2 + 1) */
typedef struct {
    int64_t re;
    int64_t im;
} fp2_t;

/* Структура кривої у короткій формі Вейєрштрасса: y^2 = x^3 + Ax + B */
typedef struct {
    fp2_t a;
    fp2_t b;
} curve_t;

/* Модульна арифметика F_p */
static inline int64_t mod_p(int64_t a) {
    int64_t r = a % P_PRIME;
    return r < 0 ? r + P_PRIME : r;
}

static int64_t exp_mod(int64_t base, int64_t exp) {
    int64_t res = 1;
    base = mod_p(base);
    while (exp > 0) {
        if (exp & 1) res = mod_p(res * base);
        base = mod_p(base * base);
        exp >>= 1;
    }
    return res;
}

static inline int64_t inv_mod(int64_t a) {
    return exp_mod(a, P_PRIME - 2);
}

/* Арифметика поля F_{p^2} */
static inline fp2_t fp2_make(int64_t re, int64_t im) {
    fp2_t z = { mod_p(re), mod_p(im) };
    return z;
}

static inline bool fp2_eq(fp2_t a, fp2_t b) {
    return a.re == b.re && a.im == b.im;
}

static inline fp2_t fp2_add(fp2_t a, fp2_t b) {
    return fp2_make(a.re + b.re, a.im + b.im);
}

static inline fp2_t fp2_sub(fp2_t a, fp2_t b) {
    return fp2_make(a.re - b.re, a.im - b.im);
}

static inline fp2_t fp2_mul(fp2_t a, fp2_t b) {
    /* (a0 + a1*i)*(b0 + b1*i) = (a0*b0 - a1*b1) + (a0*b1 + a1*b0)*i */
    int64_t r = mod_p(a.re * b.re - a.im * b.im);
    int64_t i = mod_p(a.re * b.im + a.im * b.re);
    return fp2_make(r, i);
}

static inline fp2_t fp2_inv(fp2_t a) {
    /* 1 / (re + im*i) = (re - im*i) / (re^2 + im^2) */
    int64_t norm = mod_p(a.re * a.re + a.im * a.im);
    int64_t inv_n = inv_mod(norm);
    return fp2_make(a.re * inv_n, -a.im * inv_n);
}

/* Обчислення j-інваріанта: j(E) = 1728 * 4A^3 / (4A^3 + 27B^2) */
bool curve_j_invariant(curve_t e, fp2_t *j_out) {
    fp2_t a3 = fp2_mul(e.a, fp2_mul(e.a, e.a));
    fp2_t b2 = fp2_mul(e.b, e.b);

    fp2_t four = fp2_make(4, 0);
    fp2_t twenty_seven = fp2_make(27, 0);
    fp2_t c1728 = fp2_make(1728, 0);

    fp2_t num = fp2_mul(c1728, fp2_mul(four, a3));
    fp2_t den = fp2_add(fp2_mul(four, a3), fp2_mul(twenty_seven, b2));

    if (den.re == 0 && den.im == 0) {
        return false; /* Сингулярна крива (Delta = 0) */
    }

    *j_out = fp2_mul(num, fp2_inv(den));
    return true;
}

/* Відновлення рівняння кривої за інваріантом j0 */
curve_t reconstruct_curve_from_j(fp2_t j0) {
    curve_t res;
    fp2_t c1728 = fp2_make(1728, 0);
    fp2_t zero = fp2_make(0, 0);

    if (fp2_eq(j0, zero)) {
        res.a = zero;
        res.b = fp2_make(1, 0); /* y^2 = x^3 + 1 */
        return res;
    }
    if (fp2_eq(j0, c1728)) {
        res.a = fp2_make(1, 0); /* y^2 = x^3 + x */
        res.b = zero;
        return res;
    }

    /* A = 3 * j0 * (1728 - j0) */
    /* B = 2 * j0 * (1728 - j0)^2 */
    fp2_t diff = fp2_sub(c1728, j0);
    fp2_t j_diff = fp2_mul(j0, diff);

    res.a = fp2_mul(fp2_make(3, 0), j_diff);
    res.b = fp2_mul(fp2_make(2, 0), fp2_mul(j_diff, diff));
    return res;
}

/* Оцінка класичного модулярного многочлена Phi_2(X, Y) у F_{p^2} */
fp2_t eval_phi2(fp2_t X, fp2_t Y) {
    fp2_t X2 = fp2_mul(X, X);
    fp2_t X3 = fp2_mul(X2, X);
    fp2_t Y2 = fp2_mul(Y, Y);
    fp2_t Y3 = fp2_mul(Y2, Y);

    fp2_t term1 = fp2_sub(fp2_add(X3, Y3), fp2_mul(X2, Y2));
    fp2_t term2 = fp2_mul(fp2_make(1488, 0), fp2_add(fp2_mul(X2, Y), fp2_mul(X, Y2)));
    fp2_t term3 = fp2_mul(fp2_make(162000, 0), fp2_add(X2, Y2));
    fp2_t term4 = fp2_mul(fp2_make(40773375, 0), fp2_mul(X, Y));
    fp2_t term5 = fp2_mul(fp2_make(mod_p(8748000000LL), 0), fp2_add(X, Y));
    fp2_t term6 = fp2_make(mod_p(157464000000000LL));

    fp2_t res = fp2_add(term1, term2);
    res = fp2_sub(res, term3);
    res = fp2_add(res, term4);
    res = fp2_add(res, term5);
    res = fp2_sub(res, term6);
    return res;
}

/* Пошук 2-ізогенних сусідів j-інваріанта шляхом розв'язання Phi_2(j_curr, Y) = 0 */
int find_2isogeny_neighbors(fp2_t j_curr, fp2_t *neighbors_out, int max_neighbors) {
    int count = 0;
    for (int64_t re = 0; re < P_PRIME && count < max_neighbors; re++) {
        for (int64_t im = 0; im < P_PRIME && count < max_neighbors; im++) {
            fp2_t cand = fp2_make(re, im);
            fp2_t val = eval_phi2(j_curr, cand);
            if (val.re == 0 && val.im == 0) {
                neighbors_out[count++] = cand;
            }
        }
    }
    return count;
}

int main(void) {
    printf("=== Аналіз еліптичних кривих та графа ізогеній (C) ===\n");
    printf("Базове поле: F_p, p = %lld\n\n", (long long)P_PRIME);

    /* 1. Тест обчислення j-інваріанта */
    curve_t c1 = { fp2_make(0, 0), fp2_make(1, 0) }; /* y^2 = x^3 + 1 */
    fp2_t j1;
    if (curve_j_invariant(c1, &j1)) {
        printf("Крива y^2 = x^3 + 1: j = (%lld + %lld*i) [Очікується: 0]\n", (long long)j1.re, (long long)j1.im);
    }

    curve_t c2 = { fp2_make(1, 0), fp2_make(0, 0) }; /* y^2 = x^3 + x */
    fp2_t j2;
    if (curve_j_invariant(c2, &j2)) {
        printf("Крива y^2 = x^3 + x: j = (%lld + %lld*i) [Очікується: 1728 mod p = %lld]\n",
               (long long)j2.re, (long long)j2.im, (long long)mod_p(1728));
    }

    /* 2. Відновлення кривої за довільним j0 */
    fp2_t j_test = fp2_make(250, 0);
    curve_t recon = reconstruct_curve_from_j(j_test);
    fp2_t j_recon;
    curve_j_invariant(recon, &j_recon);
    printf("Відновлена крива для j = 250: y^2 = x^3 + (%lld)x + (%lld) -> j(E) = %lld\n",
           (long long)recon.a.re, (long long)recon.b.re, (long long)j_recon.re);

    /* 3. Оцінка кроку 2-ізогенії через модулярний поліном */
    fp2_t j_root = fp2_make(1728, 0);
    fp2_t neighbors[10];
    int found = find_2isogeny_neighbors(j_root, neighbors, 10);
    printf("\nЗнайдено 2-ізогенних сусідів для j = 1728: %d\n", found);
    for (int i = 0; i < found; i++) {
        printf("  [Сусід %d] j = (%lld + %lld*i)\n", i + 1, (long long)neighbors[i].re, (long long)neighbors[i].im);
    }

    return 0;
}
