#include <math.h>

/* Структура для повернення результату та абсолютно точної похибки */
typedef struct {
    double val;
    double err;
} eft_pair_t;

/* Безпомилкове додавання двох чисел за умови |a| >= |b| (3 FLOPs) */
static inline eft_pair_t fast_two_sum(double a, double b) {
    double s = a + b;
    double z = s - a;
    double t = b - z;
    return (eft_pair_t){ .val = s, .err = t };
}

/* Безпомилкове додавання двох чисел довільного порядку (6 FLOPs) */
static inline eft_pair_t two_sum(double a, double b) {
    double s = a + b;
    double v = s - a;
    double z = s - v;
    double a_err = a - z;
    double b_err = b - v;
    return (eft_pair_t){ .val = s, .err = a_err + b_err };
}

/* Безпомилкове множення на базі апаратного FMA (2 FLOPs) */
static inline eft_pair_t two_prod_fma(double a, double b) {
    double p = a * b;
    double e = fma(a, b, -p);
    return (eft_pair_t){ .val = p, .err = e };
}
