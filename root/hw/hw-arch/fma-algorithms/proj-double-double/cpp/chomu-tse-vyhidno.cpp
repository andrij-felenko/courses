#include <span>
#include <cmath>
#include <cstddef>

/* Компенсований скалярний добуток Огіти-Румпа-Оїші (Dot2) */
[[nodiscard]] double comp_dot_product(std::span<const double> x,
                                      std::span<const double> y) noexcept {
    const size_t n = x.size();
    if (n == 0 || n != y.size()) return 0.0;

    eft_pair p = two_prod_fma(x[0], y[0]);
    double s = p.val;
    double c = p.err;

    for (size_t i = 1; i < n; ++i) {
        const eft_pair prod = two_prod_fma(x[i], y[i]);
        const eft_pair sum = two_sum(s, prod.val);
        s = sum.val;
        c += (sum.err + prod.err);
    }

    return s + c;
}

/* Компенсована схема Горнера для обчислення полінома */
[[nodiscard]] double comp_horner(std::span<const double> a, double x) noexcept {
    if (a.empty()) return 0.0;
    const size_t degree = a.size() - 1;
    if (degree == 0) return a[0];

    double s = a[degree];
    double c = 0.0;

    for (size_t k = degree; k > 0; --k) {
        const size_t i = k - 1;
        const eft_pair prod = two_prod_fma(s, x);
        const eft_pair sum = two_sum(prod.val, a[i]);
        s = sum.val;
        const double err_step = prod.err + sum.err;
        c = std::fma(c, x, err_step);
    }

    return s + c;
}
