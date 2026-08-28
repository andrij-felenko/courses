#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

// Модуль p = 23 (простий демонстраційний модуль для 𝔽_p)
#define MOD_P 23LL

// Арифметика елемента 𝔽_p
typedef int64_t fp_t;

static inline fp_t fp_add(fp_t a, fp_t b) {
    fp_t r = (a + b) % MOD_P;
    return r < 0 ? r + MOD_P : r;
}

static inline fp_t fp_sub(fp_t a, fp_t b) {
    fp_t r = (a - b) % MOD_P;
    return r < 0 ? r + MOD_P : r;
}

static inline fp_t fp_mul(fp_t a, fp_t b) {
    fp_t r = (a * b) % MOD_P;
    return r < 0 ? r + MOD_P : r;
}

// Елемент 𝔽_{p^2} = c0 + c1 * u, де u^2 = -1 (mod p)
typedef struct {
    fp_t c0;
    fp_t c1;
} fp2_t;

fp2_t fp2_add(fp2_t a, fp2_t b) {
    return (fp2_t){ fp_add(a.c0, b.c0), fp_add(a.c1, b.c1) };
}

fp2_t fp2_sub(fp2_t a, fp2_t b) {
    return (fp2_t){ fp_sub(a.c0, b.c0), fp_sub(a.c1, b.c1) };
}

// Множення: (a0 + a1*u)(b0 + b1*u) = (a0*b0 - a1*b1) + (a0*b1 + a1*b0)*u
fp2_t fp2_mul(fp2_t a, fp2_t b) {
    fp_t t0 = fp_mul(a.c0, b.c0);
    fp_t t1 = fp_mul(a.c1, b.c1);
    fp_t t2 = fp_mul(fp_add(a.c0, a.c1), fp_add(b.c0, b.c1));
    
    fp_t c0 = fp_sub(t0, t1);
    fp_t c1 = fp_sub(t2, fp_add(t0, t1));
    return (fp2_t){ c0, c1 };
}

fp2_t fp2_sqr(fp2_t a) {
    return fp2_mul(a, a);
}

// Точка на твістованій кривій E'(𝔽_{p^2}) в афінних координатах
typedef struct {
    fp2_t x;
    fp2_t y;
    bool is_infinity;
} point_g2_t;

// Розтвістована точка E(𝔽_{p^{12}}) подається розрідженими коефіцієнтами
typedef struct {
    fp2_t x_coeff; // Коефіцієнт при w^2
    fp2_t y_coeff; // Коефіцієнт при w^3
    bool is_infinity;
} untwisted_point_t;

// Перетворення точки D-type твісту: (x', y') -> (x' * w^2, y' * w^3)
untwisted_point_t sextic_untwist_d(const point_g2_t* p) {
    untwisted_point_t res;
    if (p->is_infinity) {
        res.is_infinity = true;
        res.x_coeff = (fp2_t){0, 0};
        res.y_coeff = (fp2_t){0, 0};
        return res;
    }
    
    res.is_infinity = false;
    res.x_coeff = p->x;
    res.y_coeff = p->y;
    return res;
}

// Перевірка рівняння твістованої кривої: y'^2 == x'^3 + b_twist
bool point_g2_is_valid(const point_g2_t* p, fp2_t b_twist) {
    if (p->is_infinity) return true;
    
    fp2_t lhs = fp2_sqr(p->y);
    fp2_t rhs = fp2_add(fp2_mul(fp2_sqr(p->x), p->x), b_twist);
    
    return (lhs.c0 == rhs.c0) && (lhs.c1 == rhs.c1);
}

int main(void) {
    // b_twist = (4, 0) ∈ 𝔽_{p^2}
    fp2_t b_twist = {4, 0};
    
    // Створення точки на твістованій кривій
    point_g2_t p = {
        .x = {1, 2},
        .y = {3, 4},
        .is_infinity = false
    };
    
    bool valid = point_g2_is_valid(&p, b_twist);
    printf("Валідність точки G2: %s\n", valid ? "ТАК" : "НІ");
    
    untwisted_point_t untwisted = sextic_untwist_d(&p);
    printf("Розтвістовані коефіцієнти:\n");
    printf("  X (біля w^2): %lld + %lld*u\n", untwisted.x_coeff.c0, untwisted.x_coeff.c1);
    printf("  Y (біля w^3): %lld + %lld*u\n", untwisted.y_coeff.c0, untwisted.y_coeff.c1);
    
    return 0;
}
