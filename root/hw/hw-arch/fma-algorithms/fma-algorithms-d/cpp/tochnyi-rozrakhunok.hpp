#include <cmath>

/* Точний розрахунок дискримінанта квадратного рівняння D = b^2 - 4ac */
[[nodiscard]] constexpr double accurate_discriminant(double a, double b, double c) noexcept {
    const double four_a = 4.0 * a;
    const double p = four_a * c;
    const double dp = std::fma(four_a, c, -p);
    const double d = std::fma(b, b, -p);
    return d - dp;
}
