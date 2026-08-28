#include <iostream>
#include <vector>
#include <span>
#include <limits>
#include <algorithm>
#include <numeric>
#include <execution>

struct Metrics {
    long long count{0};
    double sum{0.0};
    double min_val{std::numeric_limits<double>::infinity()};
    double max_val{-std::numeric_limits<double>::infinity()};
    double m2{0.0};

    [[nodiscard]] static constexpr Metrics empty() noexcept {
        return {};
    }

    [[nodiscard]] static constexpr Metrics from_value(double x) noexcept {
        return Metrics{1, x, x, x, 0.0};
    }

    [[nodiscard]] double mean() const noexcept {
        return count > 0 ? sum / static_cast<double>(count) : 0.0;
    }

    [[nodiscard]] double variance() const noexcept {
        return count > 1 ? m2 / static_cast<double>(count) : 0.0;
    }
};

/* Асоціативна моноїдна операція злиття */
[[nodiscard]] Metrics operator+(const Metrics& a, const Metrics& b) noexcept {
    if (a.count == 0) return b;
    if (b.count == 0) return a;

    const long long total_count = a.count + b.count;
    const double delta = b.mean() - a.mean();
    const double term = delta * delta * (static_cast<double>(a.count) * static_cast<double>(b.count) / static_cast<double>(total_count));

    return Metrics{
        .count = total_count,
        .sum = a.sum + b.sum,
        .min_val = std::min(a.min_val, b.min_val),
        .max_val = std::max(a.max_val, b.max_val),
        .m2 = a.m2 + b.m2 + term
    };
}

/* Узагальнене паралельне згортання за допомогою std::transform_reduce */
[[nodiscard]] Metrics parallel_metrics_reduce(std::span<const double> data) {
    return std::transform_reduce(
        std::execution::par_unseq,
        data.begin(), data.end(),
        Metrics::empty(),
        std::plus<Metrics>{},
        Metrics::from_value
    );
}
