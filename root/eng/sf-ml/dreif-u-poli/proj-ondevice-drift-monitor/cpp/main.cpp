#include <cstdint>
#include <cmath>
#include <array>
#include <span>
#include <concepts>
#include <algorithm>
#include <numeric>
#include <iostream>

namespace avionics::streaming {

inline constexpr float kEpsilon = 1e-7f;
inline constexpr std::size_t kAdwinMaxBuckets = 64;
inline constexpr std::size_t kAdwinBucketDegree = 5;

// ── 1. CUSUM DETECTOR ───────────────────────────────────────────────────────

template <std::floating_point T = float>
class CusumDetector final {
public:
    struct AlarmState {
        bool positive_drift{false};
        bool negative_drift{false};
        [[nodiscard]] constexpr bool triggered() const noexcept {
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

// ── 2. ADWIN DETECTOR ───────────────────────────────────────────────────────

template <std::floating_point T = float>
class AdwinDetector final {
public:
    struct Bucket {
        std::uint32_t size{0};
        T total{T{0}};
    };

    explicit constexpr AdwinDetector(T confidence_delta = T{0.002}) noexcept
        : delta_{confidence_delta} {}

    void reset() noexcept {
        bucket_count_ = 0;
        total_elements_ = 0;
        total_sum_ = T{0};
    }

    [[nodiscard]] bool update(T x_val) noexcept {
        if (bucket_count_ >= kAdwinMaxBuckets) {
            drop_oldest_bucket();
        }

        buckets_[bucket_count_] = Bucket{.size = 1, .total = x_val};
        ++bucket_count_;
        total_elements_ += 1;
        total_sum_ += x_val;

        compress_buckets();

        bool drift_detected = false;
        std::size_t cut_idx = 0;

        while (check_cut(cut_idx)) {
            drift_detected = true;
            for (std::size_t k = 0; k <= cut_idx; ++k) {
                drop_oldest_bucket();
            }
        }

        return drift_detected;
    }

    [[nodiscard]] constexpr std::uint32_t total_elements() const noexcept { return total_elements_; }
    [[nodiscard]] constexpr T current_mean() const noexcept {
        return total_elements_ > 0 ? (total_sum_ / static_cast<T>(total_elements_)) : T{0};
    }

private:
    void drop_oldest_bucket() noexcept {
        if (bucket_count_ == 0) return;
        total_elements_ -= buckets_[0].size;
        total_sum_ -= buckets_[0].total;

        for (std::size_t i = 0; i < bucket_count_ - 1; ++i) {
            buckets_[i] = buckets_[i + 1];
        }
        --bucket_count_;
    }

    void compress_buckets() noexcept {
        std::uint32_t cur_size = 1;
        std::size_t i = bucket_count_;

        while (i > 0) {
            std::size_t count_same = 0;
            int idx = static_cast<int>(i) - 1;
            while (idx >= 0 && buckets_[idx].size == cur_size) {
                ++count_same;
                --idx;
            }

            if (count_same > kAdwinBucketDegree) {
                const auto merge_idx = static_cast<std::size_t>(idx + 1);
                buckets_[merge_idx].size *= 2;
                buckets_[merge_idx].total += buckets_[merge_idx + 1].total;

                for (std::size_t k = merge_idx + 1; k < bucket_count_ - 1; ++k) {
                    buckets_[k] = buckets_[k + 1];
                }
                --bucket_count_;
            } else {
                cur_size *= 2;
                i = static_cast<std::size_t>(idx + 1);
            }
        }
    }

    [[nodiscard]] bool check_cut(std::size_t& cut_bucket_idx) const noexcept {
        if (bucket_count_ < 2 || total_elements_ < 10) return false;

        std::uint32_t n0 = 0;
        T sum0{T{0}};

        for (std::size_t i = 0; i < bucket_count_ - 1; ++i) {
            n0 += buckets_[i].size;
            sum0 += buckets_[i].total;

            const std::uint32_t n1 = total_elements_ - n0;
            const T sum1 = total_sum_ - sum0;

            if (n0 >= 4 && n1 >= 4) {
                const T mu0 = sum0 / static_cast<T>(n0);
                const T mu1 = sum1 / static_cast<T>(n1);
                const T diff = std::abs(mu0 - mu1);

                const T m = T{1} / ((T{1} / static_cast<T>(n0)) + (T{1} / static_cast<T>(n1)));
                const T eps_cut = std::sqrt((T{1} / (T{2} * m)) * std::log(T{4} / delta_));

                if (diff >= eps_cut) {
                    cut_bucket_idx = i;
                    return true;
                }
            }
        }
        return false;
    }

    std::array<Bucket, kAdwinMaxBuckets> buckets_{};
    std::size_t bucket_count_{0};
    std::uint32_t total_elements_{0};
    T total_sum_{T{0}};
    T delta_{T{0.002}};
};

// ── 3. WELFORD ACCUMULATOR & ENTROPY ───────────────────────────────────────

template <std::floating_point T = float>
class WelfordAccumulator final {
public:
    constexpr void update(T x) noexcept {
        ++count_;
        const T delta = x - mean_;
        mean_ += delta / static_cast<T>(count_);
        const T delta2 = x - mean_;
        m2_ += delta * delta2;
    }

    [[nodiscard]] constexpr T mean() const noexcept { return mean_; }
    [[nodiscard]] constexpr T variance() const noexcept {
        return count_ > 1 ? (m2_ / static_cast<T>(count_ - 1)) : T{0};
    }
    [[nodiscard]] constexpr std::uint32_t count() const noexcept { return count_; }

private:
    std::uint32_t count_{0};
    T mean_{T{0}};
    T m2_{T{0}};
};

template <std::floating_point T = float>
[[nodiscard]] T compute_normalized_entropy(std::span<const T> logits) noexcept {
    if (logits.empty()) return T{0};
    const T max_l = *std::max_element(logits.begin(), logits.end());

    T sum_exp{T{0}};
    for (const T l : logits) sum_exp += std::exp(l - max_l);

    T entropy{T{0}};
    for (const T l : logits) {
        const T p = std::exp(l - max_l) / (sum_exp + kEpsilon);
        if (p > kEpsilon) entropy -= p * std::log(p);
    }

    const T max_ent = std::log(static_cast<T>(logits.size()));
    return (max_ent > kEpsilon) ? (entropy / max_ent) : T{0};
}

template <std::floating_point T = float>
[[nodiscard]] T compute_mahalanobis_diag(std::span<const T> z,
                                        std::span<const T> mu,
                                        std::span<const T> var) noexcept {
    if (z.size() != mu.size() || z.size() != var.size() || z.empty()) return T{0};

    T d2{T{0}};
    for (std::size_t i = 0; i < z.size(); ++i) {
        const T diff = z[i] - mu[i];
        d2 += (diff * diff) / (var[i] + kEpsilon);
    }
    return d2;
}

// ── 4. ESCALATION ENGINE ───────────────────────────────────────────────────

enum class DriftLevel : std::uint8_t {
    Nominal = 0,
    Warning = 1,
    Confirmed = 2,
    Failsafe = 3
};

template <std::floating_point T = float>
class DriftMonitorEngine final {
public:
    constexpr DriftMonitorEngine(T nominal_entropy, T ood_threshold) noexcept
        : cusum_{nominal_entropy, T{0.05}, T{4.0}},
          adwin_{T{0.002}},
          ood_threshold_{ood_threshold} {}

    DriftLevel step(std::span<const T> logits,
                    std::span<const T> embedding,
                    std::span<const T> ref_mu,
                    std::span<const T> ref_var) noexcept {
        const T norm_entropy = compute_normalized_entropy(logits);
        const T d2_mahal = compute_mahalanobis_diag(embedding, ref_mu, ref_var);
        welford_.update(norm_entropy);

        const auto cusum_alarm = cusum_.update(norm_entropy);
        const bool adwin_alarm = adwin_.update(norm_entropy);

        if (d2_mahal > ood_threshold_ * T{2}) {
            level_ = DriftLevel::Failsafe;
            cooldown_timer_ = 0;
        } else if (adwin_alarm || (cusum_alarm.positive_drift && d2_mahal > ood_threshold_)) {
            level_ = DriftLevel::Confirmed;
            cooldown_timer_ = 0;
        } else if (cusum_alarm.positive_drift || adwin_alarm) {
            if (level_ < DriftLevel::Warning) {
                level_ = DriftLevel::Warning;
            }
            cooldown_timer_ = 0;
        } else {
            if (level_ > DriftLevel::Nominal) {
                if (++cooldown_timer_ >= kCooldownTarget) {
                    level_ = static_cast<DriftLevel>(static_cast<std::uint8_t>(level_) - 1);
                    cooldown_timer_ = 0;
                    cusum_.reset();
                }
            }
        }

        return level_;
    }

    [[nodiscard]] constexpr DriftLevel level() const noexcept { return level_; }

private:
    static constexpr std::uint32_t kCooldownTarget = 100;
    CusumDetector<T> cusum_;
    AdwinDetector<T> adwin_;
    WelfordAccumulator<T> welford_{};
    T ood_threshold_{T{50}};
    DriftLevel level_{DriftLevel::Nominal};
    std::uint32_t cooldown_timer_{0};
};

} // namespace avionics::streaming

int main() {
    std::cout << "=== ТЕСТ БОРТОВОГО МОНІТОРА ДРЕЙФУ (C++20) ===\n";

    avionics::streaming::DriftMonitorEngine<float> engine{0.15f, 50.0f};

    const std::array<float, 4> ref_mu{1.0f, 2.0f, -1.0f, 0.5f};
    const std::array<float, 4> ref_var{0.2f, 0.2f, 0.2f, 0.2f};

    std::cout << "[Фаза 1] Стаціонарний вхід (100 циклів)...\n";
    for (int t = 0; t < 100; ++t) {
        const std::array<float, 3> logits{4.5f, 0.2f, 0.1f};
        const std::array<float, 4> emb{1.05f, 1.95f, -0.98f, 0.52f};
        const auto lvl = engine.step(logits, emb, ref_mu, ref_var);
        if (lvl != avionics::streaming::DriftLevel::Nominal) {
            std::cerr << "ПОМИЛКА: Несподівана тривога на такті " << t << '\n';
            return 1;
        }
    }
    std::cout << "  -> Успіх: 0 хибних тривог.\n";

    std::cout << "[Фаза 2] Стрибок ентропії (імітація засліплення)...\n";
    int alarm_tick = -1;
    for (int t = 100; t < 200; ++t) {
        const std::array<float, 3> logits{1.1f, 1.0f, 0.95f};
        const std::array<float, 4> emb{1.1f, 1.9f, -1.1f, 0.4f};
        const auto lvl = engine.step(logits, emb, ref_mu, ref_var);
        if (lvl >= avionics::streaming::DriftLevel::Warning && alarm_tick == -1) {
            alarm_tick = t;
            std::cout << "  -> Тривогу зафіксовано на такті " << t << '\n';
        }
    }

    if (alarm_tick != -1 && alarm_tick <= 125) {
        std::cout << "  -> Успіх: Дрейф виявлено за " << (alarm_tick - 100) << " тактів.\n";
    } else {
        std::cerr << "ПОМИЛКА: Занадто довга затримка детекції\n";
        return 1;
    }

    std::cout << "Усі тести C++20 пройдено успішно.\n";
    return 0;
}
