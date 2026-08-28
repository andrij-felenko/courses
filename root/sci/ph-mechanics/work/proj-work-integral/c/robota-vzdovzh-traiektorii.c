#include <stddef.h>

/* Робота вздовж траєкторії: Σ F·Δr = Σ (Fx·Δx + Fy·Δy).
   Силу на плечі беремо серединою двох відліків; знак дає сам добуток. */
double path_work(const double *x, const double *y,
                 const double *Fx, const double *Fy, size_t n) {
    double W = 0.0;
    for (size_t i = 0; i + 1 < n; ++i) {
        double dx = x[i + 1] - x[i];
        double dy = y[i + 1] - y[i];
        double fx = 0.5 * (Fx[i] + Fx[i + 1]);
        double fy = 0.5 * (Fy[i] + Fy[i + 1]);
        W += fx * dx + fy * dy;               /* скалярний добуток F·Δr */
    }
    return W;
}
