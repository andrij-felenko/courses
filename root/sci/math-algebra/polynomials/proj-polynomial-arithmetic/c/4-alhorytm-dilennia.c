#include <math.h>

/* Структура для повернення частки та остачі */
typedef struct {
    Polynomial quotient;
    Polynomial remainder;
} DivisionResult;

/* Поліноміальне ділення у стовпчик: A(x) = Q(x)*B(x) + R(x) */
DivisionResult poly_divide(const Polynomial *a, const Polynomial *b) {
    DivisionResult res;
    memset(&res, 0, sizeof(res));
    
    if (!a || !b || !b->coeffs || fabs(b->coeffs[b->degree]) < 1e-12) {
        return res; // Помилка: дільник є нульовим многочленом
    }
    
    // Якщо степінь діленого менший за степінь дільника
    if (a->degree < b->degree) {
        res.quotient = poly_create(0);
        res.remainder = poly_create(a->degree);
        memcpy(res.remainder.coeffs, a->coeffs, (a->degree + 1) * sizeof(double));
        return res;
    }
    
    size_t q_deg = a->degree - b->degree;
    res.quotient = poly_create(q_deg);
    
    // Копіюємо ділене в робочий буфер остачі
    Polynomial rem = poly_create(a->degree);
    memcpy(rem.coeffs, a->coeffs, (a->degree + 1) * sizeof(double));
    
    double lead_b = b->coeffs[b->degree];
    
    for (size_t i = a->degree; i >= b->degree; --i) {
        size_t q_idx = i - b->degree;
        double factor = rem.coeffs[i] / lead_b;
        res.quotient.coeffs[q_idx] = factor;
        
        for (size_t j = 0; j <= b->degree; ++j) {
            rem.coeffs[q_idx + j] -= factor * b->coeffs[j];
        }
        if (i == 0) break; // Захист від зациклення беззнакового size_t
    }
    
    poly_normalize(&res.quotient);
    poly_normalize(&rem);
    res.remainder = rem;
    return res;
}
