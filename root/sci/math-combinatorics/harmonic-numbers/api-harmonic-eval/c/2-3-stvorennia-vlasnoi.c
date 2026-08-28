#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <errno.h>
#include <stdbool.h>

#define C_EULER_MASCHERONI 0.57721566490153286060

typedef enum {
    HARMONIC_SUCCESS = 0,
    HARMONIC_ERR_INVALID_ARG = 1,
    HARMONIC_ERR_DOMAIN = 2,
    HARMONIC_ERR_OVERFLOW = 3
} HarmonicErrorCode;

typedef struct {
    double value;
    HarmonicErrorCode error;
    const char* description;
} HarmonicResultC;

/* Чисельне обчислення Digamma ψ(x) через центральну різницю lgamma */
static double c_digamma_num(double x) {
    if (x <= 0.0 && floor(x) == x) {
        errno = EDOM;
        return NAN;
    }
    const double h = 1e-7;
    return (lgamma(x + h) - lgamma(x - h)) / (2.0 * h);
}

HarmonicResultC c_harmonic_eval(double x) {
    HarmonicResultC res;
    res.value = NAN;
    res.error = HARMONIC_SUCCESS;
    res.description = "ОК";

    if (isnan(x) || x < 0.0) {
        res.error = HARMONIC_ERR_INVALID_ARG;
        res.description = "Аргумент x не може бути від'ємним або NaN";
        return res;
    }

    if (x == 0.0) {
        res.value = 0.0;
        return res;
    }

    errno = 0;
    double dig = c_digamma_num(x + 1.0);

    if (errno == EDOM) {
        res.error = HARMONIC_ERR_DOMAIN;
        res.description = "Помилка області визначення (Domain Error у полюсі)";
        return res;
    }

    if (errno == ERANGE || isinf(dig)) {
        res.error = HARMONIC_ERR_OVERFLOW;
        res.description = "Помилка переповнення (Overflow Error)";
        return res;
    }

    res.value = dig + C_EULER_MASCHERONI;
    return res;
}
