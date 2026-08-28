#include <iostream>
#include <vector>
#include <cmath>
#include <cstdint>
#include <limits>
#include <span>
#include <algorithm>
#include <numeric>

/* Потоковий статистичний акумулятор на шаблонах C++20 */
template <typename FloatType = double>
class StreamingAccumulator {
public:
    StreamingAccumulator() noexcept { reset(); }

    void reset() noexcept {
        count_ = 0;
        mean_ = 0.0;
        M2_ = 0.0;
        M3_ = 0.0;
        M4_ = 0.0;
        min_ = std::numeric_limits<FloatType>::infinity();
        max_ = -std::numeric_limits<FloatType>::infinity();
    }

    /* Додавання одного спостереження */
    void push(FloatType x) noexcept {
        if (std::isnan(x)) return;

        ++count_;
        min_ = std::min(min_, x);
        max_ = std::max(max_, x);

        if (count_ == 1) {
            mean_ = x;
            M2_ = 0.0;
            M3_ = 0.0;
            M4_ = 0.0;
            return;
        }

        const auto n = static_cast<FloatType>(count_);
        const FloatType delta = x - mean_;
        const FloatType delta_n = delta / n;
        const FloatType delta_n2 = delta_n * delta_n;
        const FloatType term1 = delta * delta_n * (n - 1.0);

        mean_ += delta_n;

        M4_ += term1 * delta_n2 * (n * n - 3.0 * n + 3.0) +
               6.0 * delta_n2 * M2_ - 4.0 * delta_n * M3_;
        M3_ += term1 * delta_n * (n - 2.0) - 3.0 * delta_n * M2_;
        M2_ += term1;

        M2_ = std::max(static_cast<FloatType>(0.0), M2_);
        M4_ = std::max(static_cast<FloatType>(0.0), M4_);
    }

    /* Пакетне додавання через безпечний зріз std::span */
    void push_batch(std::span<const FloatType> batch) noexcept {
        for (FloatType val : batch) {
            push(val);
        }
    }

    /* Асоціативне об'єднання з іншим акумулятором */
    StreamingAccumulator& operator+=(const StreamingAccumulator& other) noexcept {
        if (other.count_ == 0) return *this;
        if (count_ == 0) {
            *this = other;
            return *this;
        }

        const auto n_a = static_cast<FloatType>(count_);
        const auto n_b = static_cast<FloatType>(other.count_);
        const FloatType n_ab = n_a + n_b;

        const FloatType delta = other.mean_ - mean_;
        const FloatType delta2 = delta * delta;
        const FloatType delta3 = delta2 * delta;
        const FloatType delta4 = delta3 * delta;

        mean_ += delta * (n_b / n_ab);

        const FloatType new_m4 = M4_ + other.M4_ +
            delta4 * (n_a * n_b * (n_a * n_a - n_a * n_b + n_b * n_b)) / (n_ab * n_ab * n_ab) +
            6.0 * delta2 * (n_a * n_a * other.M2_ + n_b * n_b * M2_) / (n_ab * n_ab) +
            4.0 * delta * (n_a * other.M3_ - n_b * M3_) / n_ab;

        const FloatType new_m3 = M3_ + other.M3_ +
            delta3 * (n_a * n_b * (n_a - n_b)) / (n_ab * n_ab) +
            3.0 * delta * (n_a * other.M2_ - n_b * M2_) / n_ab;

        const FloatType new_m2 = M2_ + other.M2_ +
            delta2 * (n_a * n_b / n_ab);

        M4_ = std::max(static_cast<FloatType>(0.0), new_m4);
        M3_ = new_m3;
        M2_ = std::max(static_cast<FloatType>(0.0), new_m2);
        count_ += other.count_;
        min_ = std::min(min_, other.min_);
        max_ = std::max(max_, other.max_);

        return *this;
    }

    [[nodiscard]] uint64_t count() const noexcept { return count_; }
    [[nodiscard]] FloatType mean() const noexcept { return mean_; }
    [[nodiscard]] FloatType min() const noexcept { return min_; }
    [[nodiscard]] FloatType max() const noexcept { return max_; }

    [[nodiscard]] FloatType sample_variance() const noexcept {
        return count_ > 1 ? M2_ / static_cast<FloatType>(count_ - 1) : 0.0;
    }

    [[nodiscard]] FloatType population_variance() const noexcept {
        return count_ > 0 ? M2_ / static_cast<FloatType>(count_) : 0.0;
    }

    [[nodiscard]] FloatType stddev() const noexcept {
        return std::sqrt(sample_variance());
    }

    [[nodiscard]] FloatType skewness() const noexcept {
        if (count_ < 3 || M2_ <= 1e-15) return 0.0;
        const auto n = static_cast<FloatType>(count_);
        const FloatType var = M2_ / n;
        return (M3_ / n) / std::pow(var, static_cast<FloatType>(1.5));
    }

    [[nodiscard]] FloatType kurtosis() const noexcept {
        if (count_ < 4 || M2_ <= 1e-15) return 0.0;
        const auto n = static_cast<FloatType>(count_);
        const FloatType var = M2_ / n;
        return (M4_ / n) / (var * var) - 3.0;
    }

private:
    uint64_t count_{0};
    FloatType mean_{0.0};
    FloatType M2_{0.0};
    FloatType M3_{0.0};
    FloatType M4_{0.0};
    FloatType min_{std::numeric_limits<FloatType>::infinity()};
    FloatType max_{-std::numeric_limits<FloatType>::infinity()};
};
