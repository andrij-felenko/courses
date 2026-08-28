#include <iostream>
#include <cstdint>
#include <cmath>
#include <span>

class WelfordAccumulator {
public:
    constexpr WelfordAccumulator() noexcept = default;

    void update(double x) noexcept {
        ++count_;
        const double delta = x - mean_;
        mean_ += delta / static_cast<double>(count_);
        const double delta2 = x - mean_;
        M2_ += delta * delta2;
    }

    void update_batch(std::span<const double> batch) noexcept {
        for (double val : batch) {
            update(val);
        }
    }

    [[nodiscard]] uint64_t count() const noexcept { return count_; }
    [[nodiscard]] double mean() const noexcept { return mean_; }

    [[nodiscard]] double variance() const noexcept {
        return count_ > 1 ? M2_ / static_cast<double>(count_ - 1) : 0.0;
    }

    [[nodiscard]] double stddev() const noexcept {
        return std::sqrt(variance());
    }

    void reset() noexcept {
        count_ = 0;
        mean_ = 0.0;
        M2_ = 0.0;
    }

private:
    uint64_t count_{0};
    double mean_{0.0};
    double M2_{0.0};
};
