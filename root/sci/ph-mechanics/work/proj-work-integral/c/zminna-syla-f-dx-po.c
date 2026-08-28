#include <stddef.h>

/* Робота змінної сили: ∫F dx методом трапецій.
   x[i] — положення (м), F[i] — сила там (Н), n — довжина логу.
   Крок Δx може бути нерівним і навіть від'ємним (рух назад). */
double trapz_work(const double *x, const double *F, size_t n) {
    double W = 0.0;
    for (size_t i = 0; i + 1 < n; ++i) {
        double dx = x[i + 1] - x[i];
        W += 0.5 * (F[i] + F[i + 1]) * dx;   /* площа однієї смужки */
    }
    return W;                                 /* Дж, якщо x у м, F у Н */
}
