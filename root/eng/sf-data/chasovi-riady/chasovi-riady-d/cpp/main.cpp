#include <iostream>
#include <chrono>
#include <optional>
#include <cstdint>
#include <span>

namespace metrics {

using Timestamp = std::chrono::nanoseconds;

/* Семпл часового ряду */
struct MetricSample {
    uint32_t series_id{0};
    Timestamp timestamp{0};
    double value{0.0};
};

/* Клас потокового експоненційного згладжування (EMA) */
class EmaFilter {
public:
    explicit EmaFilter(double alpha = 0.2) noexcept
        : alpha_((alpha > 0.0 && alpha <= 1.0) ? alpha : 0.2) {}

    [[nodiscard]] double update(double new_value) noexcept {
        if (!current_ema_.has_value()) {
            current_ema_ = new_value;
        } else {
            current_ema_ = (alpha_ * new_value) + ((1.0 - alpha_) * (*current_ema_));
        }
        return *current_ema_;
    }

    [[nodiscard]] std::optional<double> value() const noexcept {
        return current_ema_;
    }

    void reset() noexcept {
        current_ema_.reset();
    }

private:
    double alpha_;
    std::optional<double> current_ema_{std::nullopt};
};

/* Лінійна інтерполяція пропущеного значення */
[[nodiscard]] constexpr std::optional<double> linear_interpolate(
    const MetricSample& p1,
    const MetricSample& p2,
    Timestamp t_target) noexcept {
    if (t_target < p1.timestamp || t_target > p2.timestamp) {
        return std::nullopt;
    }
    if (p1.timestamp == p2.timestamp) {
        return p1.value;
    }

    const auto t_diff = static_cast<double>((p2.timestamp - p1.timestamp).count());
    const auto t_offset = static_cast<double>((t_target - p1.timestamp).count());
    const double ratio = t_offset / t_diff;

    return p1.value + ratio * (p2.value - p1.value);
}

} // namespace metrics
