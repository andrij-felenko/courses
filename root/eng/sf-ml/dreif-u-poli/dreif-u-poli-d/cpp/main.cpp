#include <cstdint>
#include <cmath>
#include <algorithm>
#include <span>
#include <concepts>
#include <optional>

namespace avionics::ml {

template <std::floating_point T = float>
class CusumDetector final {
public:
    struct AlarmState {
        bool positive_drift{false};
        bool negative_drift{false};
        [[nodiscard]] constexpr bool has_alarm() const noexcept {
            return positive_drift || negative_drift;
        }
    };

    constexpr CusumDetector(T nominal_mean, T slack_delta, T threshold) noexcept
        : mu_target_{nominal_mean},
          slack_delta_{slack_delta},
          threshold_h_{threshold} {}

    constexpr void reset() noexcept {
        s_pos_ = T{0};
        s_neg_ = T{0};
        sample_count_ = 0;
    }

    [[nodiscard]] constexpr AlarmState update(T x_val) noexcept {
        ++sample_count_;

        const T diff_pos = x_val - mu_target_ - slack_delta_;
        const T diff_neg = mu_target_ - slack_delta_ - x_val;

        s_pos_ = std::max(T{0}, s_pos_ + diff_pos);
        s_neg_ = std::max(T{0}, s_neg_ + diff_neg);

        return AlarmState{
            .positive_drift = (s_pos_ >= threshold_h_),
            .negative_drift = (s_neg_ >= threshold_h_)
        };
    }

    [[nodiscard]] constexpr T positive_sum() const noexcept { return s_pos_; }
    [[nodiscard]] constexpr T negative_sum() const noexcept { return s_neg_; }
    [[nodiscard]] constexpr std::uint32_t sample_count() const noexcept { return sample_count_; }

private:
    T mu_target_;
    T slack_delta_;
    T threshold_h_;
    T s_pos_{T{0}};
    T s_neg_{T{0}};
    std::uint32_t sample_count_{0};
};

template <std::floating_point T = float>
[[nodiscard]] T compute_normalized_entropy(std::span<const T> logits) noexcept {
    if (logits.empty()) {
        return T{0};
    }

    const T max_val = *std::max_element(logits.begin(), logits.end());
    T sum_exp{T{0}};

    for (const T logit : logits) {
        sum_exp += std::exp(logit - max_val);
    }

    constexpr T eps = T{1e-7};
    T entropy{T{0}};

    for (const T logit : logits) {
        const T p = std::exp(logit - max_val) / (sum_exp + eps);
        if (p > eps) {
            entropy -= p * std::log(p);
        }
    }

    const T max_entropy = std::log(static_cast<T>(logits.size()));
    return (max_entropy > eps) ? (entropy / max_entropy) : T{0};
}

} // namespace avionics::ml
