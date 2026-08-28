#include <math.h>

typedef struct { double hi, lo; } dd_t;

/* Швидке додавання з умовою |a| >= |b| */
static inline dd_t fast_two_sum(double a, double b) {
    double s = a + b;
    double z = s - a;
    return (dd_t){ .hi = s, .lo = b - z };
}

/* Множення double-double з використанням апаратного FMA */
static inline dd_t dd_mul(dd_t a, dd_t b) {
    double p = a.hi * b.hi;
    double e = fma(a.hi, b.hi, -p);
    double cross = fma(a.hi, b.lo, a.lo * b.hi);
    return fast_two_sum(p, e + cross);
}
