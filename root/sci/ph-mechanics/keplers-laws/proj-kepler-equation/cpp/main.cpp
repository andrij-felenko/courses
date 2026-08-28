#include <cmath>
#include <cstdio>
constexpr double PI = 3.14159265358979323846;

// M = E − e·sinE  →  E.  Робастний старт E₀ = π для великих e (комети).
double solve_kepler(double M, double e, double tol = 1e-12, int max_iter = 100) {
    M = std::fmod(M, 2 * PI);
    if (M < 0) M += 2 * PI;                        // fmod може дати відʼємне — вирівнюємо
    bool flip = M > PI;
    if (flip) M = 2 * PI - M;                      // симетрія: рахуємо на [0, π]
    double E = (e > 0.8) ? PI : M + e * std::sin(M);   // початкове наближення
    for (int i = 0; i < max_iter; ++i) {
        double dE = (E - e * std::sin(E) - M) / (1 - e * std::cos(E));
        E -= dE;
        if (std::fabs(dE) < tol) break;            // квадратична збіжність
    }
    return flip ? 2 * PI - E : E;
}

struct Vec2 { double x, y; };

// (x, y) відносно Сонця; +x — на перигелій.
Vec2 orbit_xy(double a, double e, double T, double t, double t0 = 0.0) {
    double M = 2 * PI * (t - t0) / T;              // середня аномалія
    double E = solve_kepler(M, e);
    return { a * (std::cos(E) - e), a * std::sqrt(1 - e * e) * std::sin(E) };
}

int main() {
    Vec2 p = orbit_xy(1.524, 0.0934, 686.98, 100.0);   // Марс, +100 діб
    double r  = std::hypot(p.x, p.y);
    double nu = std::atan2(p.y, p.x) * 180 / PI;
    std::printf("x=%.4f  y=%.4f  r=%.4f а.о.  nu=%.2f\n", p.x, p.y, r, nu);
    // → x=0.6902  y=1.2709  r=1.4462 а.о.  nu=61.49
    return 0;
}
