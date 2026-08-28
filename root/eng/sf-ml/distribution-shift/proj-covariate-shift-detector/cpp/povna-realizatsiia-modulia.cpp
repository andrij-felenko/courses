#include <array>
#include <span>
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <expected>
#include <numeric>

namespace embedded_ml {

enum class SafetyStatus : uint8_t {
    Nominal  = 0,
    Warning  = 1,
    Critical = 2
};

enum class DetectorError : uint8_t {
    InvalidConfiguration,
    BufferNotFull,
    InvalidDimension
};

struct DiagnosticReport {
    float max_wasserstein_w1;
    float max_ks_statistic;
    float mmd_squared;
    SafetyStatus status;
};

template <std::size_t MaxSamples = 64, std::size_t MaxDim = 16>
class CovariateShiftDetector final {
    static_assert(MaxSamples >= 4 && MaxSamples <= 256, "Sample count must be bounded for deterministic execution");
    static_assert(MaxDim >= 1 && MaxDim <= 64, "Feature dimension must fit embedded cache lines");

public:
    struct Config {
        float w1_warning{0.15f};
        float w1_critical{0.35f};
        float mmd_warning{0.08f};
        float mmd_critical{0.20f};
        float rbf_gamma{0.50f};
        std::size_t sample_count{MaxSamples};
        std::size_t feature_dim{MaxDim};
    };

    constexpr explicit CovariateShiftDetector(const Config& cfg) noexcept
        : config_(cfg), ring_head_(0), current_count_(0), cached_k_xx_(0.0f), is_initialized_(false) {}

    [[nodiscard]] std::expected<void, DetectorError> initialize(
        std::span<const float> reference_dataset
    ) noexcept {
        if (reference_dataset.size() != config_.sample_count * config_.feature_dim) {
            return std::unexpected(DetectorError::InvalidConfiguration);
        }
        if (config_.sample_count > MaxSamples || config_.feature_dim > MaxDim || config_.rbf_gamma <= 0.0f) {
            return std::unexpected(DetectorError::InvalidConfiguration);
        }

        for (std::size_t i = 0; i < config_.sample_count; ++i) {
            for (std::size_t d = 0; d < config_.feature_dim; ++d) {
                ref_samples_[i][d] = reference_dataset[i * config_.feature_dim + d];
            }
        }

        cached_k_xx_ = compute_internal_k_xx();
        ring_head_ = 0;
        current_count_ = 0;
        is_initialized_ = true;

        return {};
    }

    [[nodiscard]] std::expected<void, DetectorError> push_sample(
        std::span<const float> sample_vector
    ) noexcept {
        if (!is_initialized_ || sample_vector.size() != config_.feature_dim) {
            return std::unexpected(DetectorError::InvalidDimension);
        }

        const std::size_t head = ring_head_;
        for (std::size_t d = 0; d < config_.feature_dim; ++d) {
            stream_ring_buffer_[head][d] = sample_vector[d];
        }

        ring_head_ = (head + 1) % config_.sample_count;
        if (current_count_ < config_.sample_count) {
            ++current_count_;
        }

        return {};
    }

    [[nodiscard]] std::expected<DiagnosticReport, DetectorError> evaluate() const noexcept {
        if (!is_initialized_) {
            return std::unexpected(DetectorError::InvalidConfiguration);
        }
        if (current_count_ < config_.sample_count) {
            return std::unexpected(DetectorError::BufferNotFull);
        }

        float max_w1 = 0.0f;
        float max_ks = 0.0f;

        for (std::size_t d = 0; d < config_.feature_dim; ++d) {
            const float w1 = compute_channel_w1(d);
            const float ks = compute_channel_ks(d);
            max_w1 = std::max(max_w1, w1);
            max_ks = std::max(max_ks, ks);
        }

        const float mmd2 = compute_mmd_squared();

        SafetyStatus status = SafetyStatus::Nominal;
        if (mmd2 >= config_.mmd_critical || max_w1 >= config_.w1_critical) {
            status = SafetyStatus::Critical;
        } else if (mmd2 >= config_.mmd_warning || max_w1 >= config_.w1_warning) {
            status = SafetyStatus::Warning;
        }

        return DiagnosticReport{
            .max_wasserstein_w1 = max_w1,
            .max_ks_statistic   = max_ks,
            .mmd_squared        = mmd2,
            .status             = status
        };
    }

private:
    [[nodiscard]] float compute_sq_dist(
        std::span<const float> a,
        std::span<const float> b
    ) const noexcept {
        float sum = 0.0f;
        for (std::size_t d = 0; d < config_.feature_dim; ++d) {
            const float diff = a[d] - b[d];
            sum += diff * diff;
        }
        return sum;
    }

    [[nodiscard]] inline float rbf_kernel(
        std::span<const float> a,
        std::span<const float> b
    ) const noexcept {
        const float sq = compute_sq_dist(a, b);
        return std::exp(-config_.rbf_gamma * sq);
    }

    [[nodiscard]] float compute_internal_k_xx() const noexcept {
        const std::size_t n = config_.sample_count;
        if (n < 2) return 0.0f;

        float sum = 0.0f;
        for (std::size_t i = 0; i < n; ++i) {
            for (std::size_t j = 0; j < n; ++j) {
                if (i != j) {
                    sum += rbf_kernel(ref_samples_[i], ref_samples_[j]);
                }
            }
        }
        return sum / static_cast<float>(n * (n - 1));
    }

    [[nodiscard]] float compute_channel_w1(std::size_t channel) const noexcept {
        const std::size_t n = config_.sample_count;
        std::array<float, MaxSamples> s_ref{};
        std::array<float, MaxSamples> s_cur{};

        for (std::size_t i = 0; i < n; ++i) {
            s_ref[i] = ref_samples_[i][channel];
            s_cur[i] = stream_ring_buffer_[i][channel];
        }

        std::sort(s_ref.begin(), s_ref.begin() + n);
        std::sort(s_cur.begin(), s_cur.begin() + n);

        float sum_diff = 0.0f;
        for (std::size_t i = 0; i < n; ++i) {
            sum_diff += std::abs(s_ref[i] - s_cur[i]);
        }
        return sum_diff / static_cast<float>(n);
    }

    [[nodiscard]] float compute_channel_ks(std::size_t channel) const noexcept {
        const std::size_t n = config_.sample_count;
        std::array<float, MaxSamples> s_ref{};
        std::array<float, MaxSamples> s_cur{};

        for (std::size_t i = 0; i < n; ++i) {
            s_ref[i] = ref_samples_[i][channel];
            s_cur[i] = stream_ring_buffer_[i][channel];
        }

        std::sort(s_ref.begin(), s_ref.begin() + n);
        std::sort(s_cur.begin(), s_cur.begin() + n);

        float d_max = 0.0f;
        std::size_t i = 0;
        std::size_t j = 0;
        const float step = 1.0f / static_cast<float>(n);

        while (i < n && j < n) {
            const float cdf_ref = static_cast<float>(i + 1) * step;
            const float cdf_cur = static_cast<float>(j + 1) * step;

            if (sorted_ref[i] < sorted_cur[j]) {
                d_max = std::max(d_max, std::abs(cdf_ref - static_cast<float>(j) * step));
                ++i;
            } else if (sorted_ref[i] > sorted_cur[j]) {
                d_max = std::max(d_max, std::abs(static_cast<float>(i) * step - cdf_cur));
                ++j;
            } else {
                d_max = std::max(d_max, std::abs(cdf_ref - cdf_cur));
                ++i;
                ++j;
            }
        }
        return d_max;
    }

    [[nodiscard]] float compute_mmd_squared() const noexcept {
        const std::size_t n = config_.sample_count;
        const float gamma = config_.rbf_gamma;

        float sum_xy = 0.0f;
        for (std::size_t i = 0; i < n; ++i) {
            for (std::size_t j = 0; j < n; ++j) {
                sum_xy += rbf_kernel(ref_samples_[i], stream_ring_buffer_[j]);
            }
        }
        const float k_xy = sum_xy / static_cast<float>(n * n);

        float sum_yy = 0.0f;
        for (std::size_t i = 0; i < n; ++i) {
            for (std::size_t j = 0; j < n; ++j) {
                if (i != j) {
                    sum_yy += rbf_kernel(stream_ring_buffer_[i], stream_ring_buffer_[j]);
                }
            }
        }
        const float k_yy = sum_yy / static_cast<float>(n * (n - 1));

        const float mmd2 = cached_k_xx_ - 2.0f * k_xy + k_yy;
        return (mmd2 > 0.0f) ? mmd2 : 0.0f;
    }

    Config config_;
    std::array<std::array<float, MaxDim>, MaxSamples> ref_samples_{};
    std::array<std::array<float, MaxDim>, MaxSamples> stream_ring_buffer_{};
    std::size_t ring_head_;
    std::size_t current_count_;
    float cached_k_xx_;
    bool is_initialized_;
};

} // namespace embedded_ml
