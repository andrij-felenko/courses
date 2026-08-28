#include <stdio.h>
#include <stddef.h>

/* Обчислення значення многочлена P(x) за схемою Горнера.
   coeffs: вказівник на масив коефіцієнтів [a0, a1, ..., an].
   deg: степінь многочлена n (розмір масиву становить deg + 1).
   x: аргумент, у якому обчислюється значення.
   Часова складність: O(n), просторова складність: O(1). */
double polynomial_eval_horner(const double *coeffs, size_t deg, double x) {
    if (coeffs == NULL) {
        return 0.0;
    }
    double result = coeffs[deg];
    for (size_t i = deg; i > 0; --i) {
        result = result * x + coeffs[i - 1];
    }
    return result;
}
