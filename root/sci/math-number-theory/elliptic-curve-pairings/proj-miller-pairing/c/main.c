#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

// Модуль іграшкового поля F_19
#define MOD 19

// Елемент поля F_19
typedef int32_t fp_t;

static inline fp_t fp_add(fp_t a, fp_t b) {
    fp_t r = (a + b) % MOD;
    return r < 0 ? r + MOD : r;
}

static inline fp_t fp_sub(fp_t a, fp_t b) {
    fp_t r = (a - b) % MOD;
    return r < 0 ? r + MOD : r;
}

static inline fp_t fp_mul(fp_t a, fp_t b) {
    fp_t r = (a * b) % MOD;
    return r < 0 ? r + MOD : r;
}

static fp_t fp_inv(fp_t a) {
    a = (a % MOD + MOD) % MOD;
    for (fp_t x = 1; x < MOD; x++) {
        if ((a * x) % MOD == 1) return x;
    }
    return 0; // Не існує
}

// Елемент розширення F_{19^2} = F_19[i] / (i^2 + 1)
typedef struct {
    fp_t re;
    fp_t im;
} fp2_t;

static fp2_t fp2_add(fp2_t a, fp2_t b) {
    return (fp2_t){ fp_add(a.re, b.re), fp_add(a.im, b.im) };
}

static fp2_t fp2_sub(fp2_t a, fp2_t b) {
    return (fp2_t){ fp_sub(a.re, b.re), fp_sub(a.im, b.im) };
}

// (a + b*i)*(c + d*i) = (a*c - b*d) + (a*d + b*c)*i
static fp2_t fp2_mul(fp2_t a, fp2_t b) {
    fp_t re = fp_sub(fp_mul(a.re, b.re), fp_mul(a.im, b.im));
    fp_t im = fp_add(fp_mul(a.re, b.im), fp_mul(a.im, b.re));
    return (fp2_t){ re, im };
}

static fp2_t fp2_sqr(fp2_t a) {
    return fp2_mul(a, a);
}

static fp2_t fp2_inv(fp2_t a) {
    // 1 / (a + b*i) = (a - b*i) / (a^2 + b^2)
    fp_t norm = fp_add(fp_mul(a.re, a.re), fp_mul(a.im, a.im));
    fp_t inv_norm = fp_inv(norm);
    return (fp2_t){ fp_mul(a.re, inv_norm), fp_mul(fp_sub(0, a.im), inv_norm) };
}

// Точка на кривій над F_192
typedef struct {
    fp2_t x;
    fp2_t y;
    bool infinity;
} point_fp2_t;

// Обчислення дотичної або січної прямої l(Q) / v(Q)
static fp2_t eval_line_and_step(point_fp2_t *T, const point_fp2_t *P, const point_fp2_t *Q) {
    if (T->infinity) return (fp2_t){ 1, 0 };

    fp2_t lambda;
    if (P == NULL) { // Подвоєння T
        // lambda = 3 * x^2 / (2 * y)
        fp2_t num = fp2_mul((fp2_t){ 3, 0 }, fp2_sqr(T->x));
        fp2_t den = fp2_mul((fp2_t){ 2, 0 }, T->y);
        lambda = fp2_mul(num, fp2_inv(den));
    } else { // Додавання P до T
        // lambda = (y2 - y1) / (x2 - x1)
        fp2_t num = fp2_sub(P->y, T->y);
        fp2_t den = fp2_sub(P->x, T->x);
        lambda = fp2_mul(num, fp2_inv(den));
    }

    // Рівняння прямої: l(Q) = (y_Q - y_T) - lambda * (x_Q - x_T)
    fp2_t dx = fp2_sub(Q->x, T->x);
    fp2_t dy = fp2_sub(Q->y, T->y);
    fp2_t l_val = fp2_sub(dy, fp2_mul(lambda, dx));

    // Оновлюємо нову точку T = T + P
    fp2_t x3 = fp2_sub(fp2_sub(fp2_sqr(lambda), T->x), (P ? P->x : T->x));
    fp2_t y3 = fp2_sub(fp2_mul(lambda, fp2_sub(T->x, x3)), T->y);
    T->x = x3;
    T->y = y3;

    return l_val;
}

// Фінальне піднесення до степеня: f^((19^2 - 1) / r)
static fp2_t final_exponentiation(fp2_t f, int32_t r) {
    int32_t exp = (MOD * MOD - 1) / r; // (361 - 1) / 3 = 120
    fp2_t res = { 1, 0 };
    fp2_t base = f;

    while (exp > 0) {
        if (exp & 1) res = fp2_mul(res, base);
        base = fp2_sqr(base);
        exp >>= 1;
    }
    return res;
}

// Головна функція спарювання Тейта
fp2_t tate_pairing(point_fp2_t P, point_fp2_t Q, int32_t r) {
    point_fp2_t T = P;
    fp2_t f = { 1, 0 };

    // Цикл Міллера для r = 3 (двійковий розклад: 11_2)
    for (int i = 1; i >= 0; i--) {
        fp2_t l_double = eval_line_and_step(&T, NULL, &Q);
        f = fp2_mul(fp2_sqr(f), l_double);

        if (i == 0) { // Старший біт оброблено, додаємо P
            fp2_t l_add = eval_line_and_step(&T, &P, &Q);
            f = fp2_mul(f, l_add);
        }
    }

    return final_exponentiation(f, r);
}

int main(void) {
    // Точка P = (0, 1) над F_19
    point_fp2_t P = { {0, 0}, {1, 0}, false };
    // Точка Q = (8, 6i) над F_19^2
    point_fp2_t Q = { {8, 0}, {0, 6}, false };

    fp2_t res = tate_pairing(P, Q, 3);
    printf("Результат спарювання e(P, Q) = %d + %d*i\n", res.re, res.im);
    return 0;
}
