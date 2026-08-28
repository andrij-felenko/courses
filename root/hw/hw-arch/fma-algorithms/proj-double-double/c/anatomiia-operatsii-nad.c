#include <math.h>
#include <stdbool.h>

typedef struct {
    double hi;
    double lo;
} dd_real_t;

/* Створення числа double-double із звичайного double */
static inline dd_real_t dd_from_double(double x) {
    return (dd_real_t){ .hi = x, .lo = 0.0 };
}

/* Додавання двох чисел double-double: (a.hi + a.lo) + (b.hi + b.lo) */
static inline dd_real_t dd_add(dd_real_t a, dd_real_t b) {
    eft_pair_t s = two_sum(a.hi, b.hi);
    eft_pair_t t = two_sum(a.lo, b.lo);
    double c = s.err + t.val;
    eft_pair_t v = fast_two_sum(s.val, c);
    double w = t.err + v.err;
    eft_pair_t res = fast_two_sum(v.val, w);
    return (dd_real_t){ .hi = res.val, .lo = res.err };
}

/* Віднімання двох чисел double-double */
static inline dd_real_t dd_sub(dd_real_t a, dd_real_t b) {
    dd_real_t neg_b = { .hi = -b.hi, .lo = -b.lo };
    return dd_add(a, neg_b);
}

/* Множення двох чисел double-double з використанням FMA */
static inline dd_real_t dd_mul(dd_real_t a, dd_real_t b) {
    eft_pair_t p = two_prod_fma(a.hi, b.hi);
    /* Додаємо перехресні добутки */
    double cross = fma(a.hi, b.lo, a.lo * b.hi);
    double total_lo = p.err + cross;
    eft_pair_t res = fast_two_sum(p.val, total_lo);
    return (dd_real_t){ .hi = res.val, .lo = res.err };
}

/* Ділення двох чисел double-double */
static inline dd_real_t dd_div(dd_real_t a, dd_real_t b) {
    double q1 = a.hi / b.hi;
    /* Обчислюємо залишок r = a - b * q1 за допомогою FMA */
    double r_hi = fma(-b.hi, q1, a.hi);
    double r_lo = a.lo - b.lo * q1;
    double q2 = (r_hi + r_lo) / b.hi;
    eft_pair_t res = fast_two_sum(q1, q2);
    return (dd_real_t){ .hi = res.val, .lo = res.err };
}

/* Квадратний корінь числа double-double */
static inline dd_real_t dd_sqrt(dd_real_t a) {
    if (a.hi <= 0.0) {
        if (a.hi == 0.0) return (dd_real_t){ 0.0, 0.0 };
        return (dd_real_t){ NAN, NAN };
    }
    double s1 = sqrt(a.hi);
    /* Залишок r = a - s1^2 */
    double r = fma(-s1, s1, a.hi) + a.lo;
    double s2 = r / (2.0 * s1);
    eft_pair_t res = fast_two_sum(s1, s2);
    return (dd_real_t){ .hi = res.val, .lo = res.err };
}
