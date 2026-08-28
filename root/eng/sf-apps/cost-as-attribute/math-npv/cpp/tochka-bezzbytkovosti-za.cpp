#include <cmath>
#include <cstdio>

double annuity_factor(double r, int n) {
    return r == 0.0 ? static_cast<double>(n) : (1 - std::pow(1 + r, -n)) / r;
}

// Знайти r*, за якої A(r*) = target_A. A спадає з r → бісекція надійна.
double solve_rate(double target_A, int n,
                  double lo = 1e-9, double hi = 5.0, int iters = 100) {
    for (int i = 0; i < iters; ++i) {
        double mid = (lo + hi) / 2;
        if (annuity_factor(mid, n) > target_A)
            lo = mid;        // A завелика → ставка замала → рухаємось управо
        else
            hi = mid;        // A замала  → ставка завелика → рухаємось уліво
    }
    return (lo + hi) / 2;
}

int main() {
    // «будувати» = «купити»:  150 + 20·A = 60·A  ⟹  A = 3.75
    double r_star = solve_rate(3.75, 5);
    std::printf("r* = %.4f  (%.1f %%)\n", r_star, r_star * 100);   // r* = 0.1042  (10.4 %)
}
