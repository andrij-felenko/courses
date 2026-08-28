#include <stdlib.h>
#include <string.h>
#include <math.h>

typedef struct {
    double *coeffs;
    size_t degree;
} Polynomial;

/* Створення многочлена заданого степеня з ініціалізацією нулями */
Polynomial poly_create(size_t degree) {
    Polynomial p;
    p.degree = degree;
    p.coeffs = (double *)calloc(degree + 1, sizeof(double));
    return p;
}

/* Звільнення динамічної пам'яті */
void poly_free(Polynomial *p) {
    if (p && p->coeffs) {
        free(p->coeffs);
        p->coeffs = NULL;
        p->degree = 0;
    }
}

/* Нормалізація: видалення нульових коефіцієнтів на старших позиціях */
void poly_normalize(Polynomial *p) {
    if (!p || !p->coeffs) return;
    while (p->degree > 0 && fabs(p->coeffs[p->degree]) < 1e-12) {
        p->degree--;
    }
}

/* Додавання двох многочленів: C(x) = A(x) + B(x) */
Polynomial poly_add(const Polynomial *a, const Polynomial *b) {
    if (!a || !b) return poly_create(0);
    size_t max_deg = (a->degree > b->degree) ? a->degree : b->degree;
    Polynomial c = poly_create(max_deg);
    
    for (size_t i = 0; i <= max_deg; ++i) {
        double val_a = (i <= a->degree) ? a->coeffs[i] : 0.0;
        double val_b = (i <= b->degree) ? b->coeffs[i] : 0.0;
        c.coeffs[i] = val_a + val_b;
    }
    poly_normalize(&c);
    return c;
}

/* Множення двох многочленів: C(x) = A(x) * B(x) через дискретну згортку */
Polynomial poly_multiply(const Polynomial *a, const Polynomial *b) {
    if (!a || !b || !a->coeffs || !b->coeffs) {
        return poly_create(0);
    }
    size_t res_deg = a->degree + b->degree;
    Polynomial c = poly_create(res_deg);
    
    for (size_t i = 0; i <= a->degree; ++i) {
        for (size_t j = 0; j <= b->degree; ++j) {
            c.coeffs[i + j] += a->coeffs[i] * b->coeffs[j];
        }
    }
    poly_normalize(&c);
    return c;
}
