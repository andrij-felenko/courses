#include <math.h>
#include <stddef.h>

/* ── Крихітне комплексне ядро: модуль=розтяг, аргумент=поворот ────────── */
typedef struct { double re, im; } cplx;

static inline cplx c_make(double re, double im) { cplx z = {re, im}; return z; }

static inline cplx c_add(cplx a, cplx b) {
    return c_make(a.re + b.re, a.im + b.im);
}

/* добуток: модулі множаться, аргументи додаються — саме тому ланки просто перемножуємо */
static inline cplx c_mul(cplx a, cplx b) {
    return c_make(a.re * b.re - a.im * b.im,
                  a.re * b.im + a.im * b.re);
}

/* ділення a/b через множення на спряжене знаменника */
static inline cplx c_div(cplx a, cplx b) {
    double d = b.re * b.re + b.im * b.im;
    return c_make((a.re * b.re + a.im * b.im) / d,
                  (a.im * b.re - a.re * b.im) / d);
}

static inline double c_abs(cplx z) {           /* модуль = розтяг амплітуди */
    return sqrt(z.re * z.re + z.im * z.im);
}

static inline double c_arg(cplx z) {           /* аргумент = зсув фази, рад, у (−π, π] */
    return atan2(z.im, z.re);
}
