#include <algorithm>
#include <cstdint>

struct Interval {
    int64_t lo{0};
    int64_t hi{0};

    [[nodiscard]] constexpr bool contains_zero() const noexcept {
        return lo <= 0 && hi >= 0;
    }

    friend constexpr Interval operator+(Interval a, Interval b) noexcept {
        return {a.lo + b.lo, a.hi + b.hi};
    }

    friend constexpr Interval operator-(Interval a, Interval b) noexcept {
        return {a.lo - b.hi, a.hi - b.lo};
    }

    friend constexpr Interval operator*(Interval a, Interval b) noexcept {
        const int64_t p1 = a.lo * b.lo, p2 = a.lo * b.hi;
        const int64_t p3 = a.hi * b.lo, p4 = a.hi * b.hi;
        return {
            std::min({p1, p2, p3, p4}),
            std::max({p1, p2, p3, p4})
        };
    }

    [[nodiscard]] constexpr Interval square() const noexcept {
        if (lo <= 0 && hi >= 0) {
            return {0, std::max(lo * lo, hi * hi)};
        }
        const int64_t m1 = lo * lo, m2 = hi * hi;
        return {std::min(m1, m2), std::max(m1, m2)};
    }
};
