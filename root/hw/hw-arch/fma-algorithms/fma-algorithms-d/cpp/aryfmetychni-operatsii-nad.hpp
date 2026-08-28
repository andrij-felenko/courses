#include <cmath>

struct dd_real {
    double hi{0.0};
    double lo{0.0};
};

[[nodiscard]] constexpr dd_real fast_two_sum(double a, double b) noexcept {
    const double s = a + b;
    const double z = s - a;
    return {s, b - z};
}

[[nodiscard]] inline dd_real operator*(const dd_real& a, const dd_real& b) noexcept {
    const double p = a.hi * b.hi;
    const double e = std::fma(a.hi, b.hi, -p);
    const double cross = std::fma(a.hi, b.lo, a.lo * b.hi);
    return fast_two_sum(p, e + cross);
}
