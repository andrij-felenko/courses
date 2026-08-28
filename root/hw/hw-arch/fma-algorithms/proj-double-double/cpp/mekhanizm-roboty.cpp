#include <cmath>
#include <utility>

struct eft_pair {
    double val{0.0};
    double err{0.0};
};

/* Безпомилкове додавання двох чисел за умови |a| >= |b| (3 FLOPs) */
[[nodiscard]] constexpr eft_pair fast_two_sum(double a, double b) noexcept {
    const double s = a + b;
    const double z = s - a;
    const double t = b - z;
    return {s, t};
}

/* Безпомилкове додавання двох чисел довільного порядку (6 FLOPs) */
[[nodiscard]] constexpr eft_pair two_sum(double a, double b) noexcept {
    const double s = a + b;
    const double v = s - a;
    const double z = s - v;
    const double a_err = a - z;
    const double b_err = b - v;
    return {s, a_err + b_err};
}

/* Безпомилкове множення на базі апаратного FMA (2 FLOPs) */
[[nodiscard]] inline eft_pair two_prod_fma(double a, double b) noexcept {
    const double p = a * b;
    const double e = std::fma(a, b, -p);
    return {p, e};
}
