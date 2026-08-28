#include <span>
#include <cmath>
#include <cstddef>

/* Компенсований скалярний добуток Dot2 на C++20 */
[[nodiscard]] double dot2(std::span<const double> x, std::span<const double> y) noexcept {
    const size_t n = x.size();
    if (n == 0 || n != y.size()) return 0.0;

    const double p = x[0] * y[0];
    double s = p;
    double c = std::fma(x[0], y[0], -p);

    for (size_t i = 1; i < n; ++i) {
        const double pi = x[i] * y[i];
        const double pi_err = std::fma(x[i], y[i], -pi);

        const double s_next = s + pi;
        const double v = s_next - s;
        const double s_err = (s - (s_next - v)) + (pi - v);

        s = s_next;
        c += (s_err + pi_err);
    }
    return s + c;
}
