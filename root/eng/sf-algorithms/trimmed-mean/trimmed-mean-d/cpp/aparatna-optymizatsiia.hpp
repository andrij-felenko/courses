#include <algorithm>

/* Олімпійське середнє N=5, k=1 у C++20 (constexpr, branchless) */
[[nodiscard]] constexpr double trimmed_mean_5_k1(double a, double b, double c, double d, double e) noexcept {
    const double total_sum = a + b + c + d + e;

    const double min1 = std::min(a, b);
    const double min2 = std::min(c, d);
    const double min12 = std::min(min1, min2);
    const double global_min = std::min(min12, e);

    const double max1 = std::max(a, b);
    const double max2 = std::max(c, d);
    const double max12 = std::max(max1, max2);
    const double global_max = std::max(max12, e);

    return (total_sum - global_min - global_max) / 3.0;
}
