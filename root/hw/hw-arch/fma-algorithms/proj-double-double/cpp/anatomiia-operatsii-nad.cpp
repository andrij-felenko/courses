#include <cmath>
#include <concepts>
#include <limits>

struct dd_real {
    double hi{0.0};
    double lo{0.0};

    constexpr dd_real() noexcept = default;
    constexpr explicit dd_real(double h, double l = 0.0) noexcept : hi(h), lo(l) {}

    [[nodiscard]] constexpr explicit operator double() const noexcept {
        return hi + lo;
    }
};

/* Додавання двох чисел double-double */
[[nodiscard]] inline dd_real operator+(const dd_real& a, const dd_real& b) noexcept {
    const eft_pair s = two_sum(a.hi, b.hi);
    const eft_pair t = two_sum(a.lo, b.lo);
    const double c = s.err + t.val;
    const eft_pair v = fast_two_sum(s.val, c);
    const double w = t.err + v.err;
    const eft_pair res = fast_two_sum(v.val, w);
    return dd_real{res.val, res.err};
}

/* Унарний мінус та віднімання */
[[nodiscard]] constexpr dd_real operator-(const dd_real& a) noexcept {
    return dd_real{-a.hi, -a.lo};
}

[[nodiscard]] inline dd_real operator-(const dd_real& a, const dd_real& b) noexcept {
    return a + (-b);
}

/* Множення з використанням FMA */
[[nodiscard]] inline dd_real operator*(const dd_real& a, const dd_real& b) noexcept {
    const eft_pair p = two_prod_fma(a.hi, b.hi);
    const double cross = std::fma(a.hi, b.lo, a.lo * b.hi);
    const double total_lo = p.err + cross;
    const eft_pair res = fast_two_sum(p.val, total_lo);
    return dd_real{res.val, res.err};
}

/* Ділення */
[[nodiscard]] inline dd_real operator/(const dd_real& a, const dd_real& b) noexcept {
    const double q1 = a.hi / b.hi;
    const double r_hi = std::fma(-b.hi, q1, a.hi);
    const double r_lo = a.lo - b.lo * q1;
    const double q2 = (r_hi + r_lo) / b.hi;
    const eft_pair res = fast_two_sum(q1, q2);
    return dd_real{res.val, res.err};
}

/* Квадратний корінь */
[[nodiscard]] inline dd_real sqrt(const dd_real& a) noexcept {
    if (a.hi <= 0.0) {
        if (a.hi == 0.0) return dd_real{0.0, 0.0};
        return dd_real{std::numeric_limits<double>::quiet_NaN(),
                       std::numeric_limits<double>::quiet_NaN()};
    }
    const double s1 = std::sqrt(a.hi);
    const double r = std::fma(-s1, s1, a.hi) + a.lo;
    const double s2 = r / (2.0 * s1);
    const eft_pair res = fast_two_sum(s1, s2);
    return dd_real{res.val, res.err};
}
