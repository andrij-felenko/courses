#include <cstddef>

// Момент інерції однорідного диска (вісь ⟂ через центр) — сітка n×n.
// Контроль: має збігтися з ½·M·R².
double disc_inertia_grid(double R, double M, std::size_t n) {
    const double step = 2.0 * R / n;          // сторона клітинки
    double s = 0.0;                           // Σ r²
    std::size_t inside = 0;
    for (std::size_t i = 0; i < n; ++i) {
        const double x = -R + (i + 0.5) * step;
        for (std::size_t j = 0; j < n; ++j) {
            const double y = -R + (j + 0.5) * step;
            const double r2 = x*x + y*y;
            if (r2 <= R*R) {                  // клітинка всередині диска?
                s += r2;
                ++inside;
            }
        }
    }
    return s * (M / inside);                   // J = Σ r²·Δm, Δm = M/влучань
}
