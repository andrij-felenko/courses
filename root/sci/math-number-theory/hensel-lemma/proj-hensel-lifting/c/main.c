#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <inttypes.h>

/* Коди повернення для операцій підйому Гензеля */
typedef enum {
    HENSEL_OK = 0,
    HENSEL_ERR_SINGULAR = -1,
    HENSEL_ERR_NO_INVERSE = -2,
    HENSEL_ERR_INVALID_PARAM = -3
} HenselStatus;

/* Безпечне приведення числа до невід'ємного залишку в кільці Z/mZ */
static inline int64_t mod_pos(int64_t val, int64_t m) {
    int64_t rem = val % m;
    return (rem < 0) ? rem + m : rem;
}

/* Обчислення модульного оберненого елемента: a * x ≡ 1 (mod m)
   використовуючи розширений алгоритм Евкліда (Extended GCD) */
static bool mod_inverse(int64_t a, int64_t m, int64_t *out_inv) {
    if (m <= 1) return false;
    int64_t m0 = m;
    int64_t y = 0, x = 1;
    int64_t curr_a = mod_pos(a, m);

    while (curr_a > 1) {
        if (m == 0) return false;
        int64_t q = curr_a / m;
        int64_t t = m;
        m = curr_a % m;
        curr_a = t;
        t = y;
        y = x - q * y;
        x = t;
    }
    if (curr_a != 1) return false;
    *out_inv = mod_pos(x, m0);
    return true;
}

/* Обчислення значення багаточлена f(x) = c_n*x^n + ... + c_0 за схемою Горнера */
static int64_t eval_poly(const int64_t *poly, size_t deg, int64_t x, int64_t mod) {
    int64_t result = 0;
    for (size_t i = deg + 1; i > 0; --i) {
        size_t idx = i - 1;
        result = mod_pos(result * x + poly[idx], mod);
    }
    return result;
}

/* Обчислення формальної похідної f'(x) за схемою Горнера за заданим модулем */
static int64_t eval_derivative(const int64_t *poly, size_t deg, int64_t x, int64_t mod) {
    if (deg == 0) return 0;
    int64_t result = 0;
    for (size_t i = deg + 1; i > 1; --i) {
        size_t idx = i - 1;
        int64_t coeff = mod_pos(poly[idx] * (int64_t)idx, mod);
        result = mod_pos(result * x + coeff, mod);
    }
    return result;
}

/* Швидке цілочисельне піднесення до степеня p^k */
static int64_t int_pow(int64_t base, int exp) {
    int64_t res = 1;
    for (int i = 0; i < exp; ++i) {
        res *= base;
    }
    return res;
}

/* Лінійний підйом Гензеля: збільшує степінь модуля p^k на 1 на кожній ітерації */
HenselStatus hensel_lift_linear(
    const int64_t *poly,
    size_t deg,
    int64_t p,
    int target_k,
    int64_t r1,
    int64_t *out_root
) {
    if (poly == NULL || out_root == NULL || target_k < 1 || p < 2) {
        return HENSEL_ERR_INVALID_PARAM;
    }

    int64_t current_root = mod_pos(r1, p);
    int64_t f_prime_mod_p = eval_derivative(poly, deg, current_root, p);

    /* Перевірка невиродженості кореня: f'(r1) ≢ 0 (mod p) */
    if (f_prime_mod_p == 0) {
        return HENSEL_ERR_SINGULAR;
    }

    int64_t v_inv = 0;
    if (!mod_inverse(f_prime_mod_p, p, &v_inv)) {
        return HENSEL_ERR_NO_INVERSE;
    }

    int64_t p_pow = p;
    for (int step = 1; step < target_k; ++step) {
        int64_t p_next = p_pow * p;
        int64_t f_val = eval_poly(poly, deg, current_root, p_next);
        int64_t q = f_val / p_pow;

        /* Обчислюємо поправку t: t ≡ -q * [f'(r1)]^-1 (mod p) */
        int64_t t = mod_pos(-q * v_inv, p);
        current_root = mod_pos(current_root + t * p_pow, p_next);
        p_pow = p_next;
    }

    *out_root = current_root;
    return HENSEL_OK;
}

/* Квадратичний підйом Гензеля (метод Ньютона з подвоєнням точності p^k -> p^(2k)) */
HenselStatus hensel_lift_quadratic(
    const int64_t *poly,
    size_t deg,
    int64_t p,
    int target_k,
    int64_t r1,
    int64_t *out_root
) {
    if (poly == NULL || out_root == NULL || target_k < 1 || p < 2) {
        return HENSEL_ERR_INVALID_PARAM;
    }

    int64_t root = mod_pos(r1, p);
    int64_t f_prime = eval_derivative(poly, deg, root, p);
    if (f_prime == 0) {
        return HENSEL_ERR_SINGULAR;
    }

    int64_t target_mod = int_pow(p, target_k);
    int64_t current_mod = p;

    while (current_mod < target_mod) {
        int64_t next_mod = current_mod * current_mod;
        int64_t f_val = eval_poly(poly, deg, root, next_mod);
        int64_t df_val = eval_derivative(poly, deg, root, next_mod);

        int64_t inv_df = 0;
        if (!mod_inverse(df_val, next_mod, &inv_df)) {
            return HENSEL_ERR_NO_INVERSE;
        }

        int64_t delta = mod_pos(f_val * inv_df, next_mod);
        root = mod_pos(root - delta, next_mod);
        current_mod = next_mod;
    }

    *out_root = mod_pos(root, target_mod);
    return HENSEL_OK;
}

int main(void) {
    printf("=== Демонстрація підйому Гензеля на C ===\n\n");

    /* Тест 1: f(x) = x^2 - 7 = 0 (mod 3^5 = 243), початковий корінь r1 = 1 (mod 3) */
    int64_t poly1[3] = {-7, 0, 1}; /* -7 + 0*x + 1*x^2 */
    size_t deg1 = 2;
    int64_t p1 = 3;
    int k1 = 5;
    int64_t root1_init = 1;
    int64_t lifted_linear = 0;

    printf("--- Тест 1: x^2 - 7 ≡ 0 (mod 3^5) ---\n");
    HenselStatus st1 = hensel_lift_linear(poly1, deg1, p1, k1, root1_init, &lifted_linear);
    if (st1 == HENSEL_OK) {
        int64_t mod_target = int_pow(p1, k1);
        printf("Лінійний підйом: корінь a_%d = %" PRId64 " (mod %" PRId64 ")\n", k1, lifted_linear, mod_target);
        int64_t check = eval_poly(poly1, deg1, lifted_linear, mod_target);
        printf("Перевірка: f(%" PRId64 ") mod %" PRId64 " = %" PRId64 " (успіх: %s)\n",
               lifted_linear, mod_target, check, (check == 0) ? "ТАК" : "НІ");
    } else {
        printf("Помилка лінійного підйому: %d\n", st1);
    }

    /* Тест 2: f(x) = x^3 - 2 = 0 (mod 5^4 = 625), початковий корінь r1 = 3 (mod 5) */
    int64_t poly2[4] = {-2, 0, 0, 1}; /* -2 + 0*x + 0*x^2 + 1*x^3 */
    size_t deg2 = 3;
    int64_t p2 = 5;
    int k2 = 4;
    int64_t root2_init = 3;
    int64_t lifted_quad = 0;

    printf("\n--- Тест 2: x^3 - 2 ≡ 0 (mod 5^4) ---\n");
    HenselStatus st2 = hensel_lift_quadratic(poly2, deg2, p2, k2, root2_init, &lifted_quad);
    if (st2 == HENSEL_OK) {
        int64_t mod_target2 = int_pow(p2, k2);
        printf("Квадратичний підйом: корінь a_%d = %" PRId64 " (mod %" PRId64 ")\n", k2, lifted_quad, mod_target2);
        int64_t check2 = eval_poly(poly2, deg2, lifted_quad, mod_target2);
        printf("Перевірка: f(%" PRId64 ") mod %" PRId64 " = %" PRId64 " (успіх: %s)\n",
               lifted_quad, mod_target2, check2, (check2 == 0) ? "ТАК" : "НІ");
    } else {
        printf("Помилка квадратичного підйому: %d\n", st2);
    }

    /* Тест 3: Вироджений (кратний) корінь f(x) = x^2 - 1 (mod 2) */
    int64_t poly3[3] = {-1, 0, 1};
    int64_t root3_init = 1;
    int64_t lifted_sing = 0;

    printf("\n--- Тест 3: Особливий корінь f'(1) = 2 ≡ 0 (mod 2) ---\n");
    HenselStatus st3 = hensel_lift_linear(poly3, 2, 2, 3, root3_init, &lifted_sing);
    if (st3 == HENSEL_ERR_SINGULAR) {
        printf("Особливий корінь успішно виявлено: f'(r1) = 0 (mod p), потрібна узагальнена лема.\n");
    }

    return 0;
}
