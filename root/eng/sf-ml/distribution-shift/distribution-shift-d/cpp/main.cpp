#include <array>
#include <span>
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <expected>

namespace embedded_safety {

inline constexpr std::size_t MaxSampleWindow = 128;

enum class ShiftStatus : uint8_t {
    Nominal  = 0,
    Warning  = 1,
    Critical = 2
};

enum class DetectionError : uint8_t {
    InvalidSize,
    BufferOverflow
};

struct ShiftMetrics {
    float wasserstein_w1;
    float ks_statistic;
    ShiftStatus status;
};

template <std::size_t N = MaxSampleWindow>
class ShiftDetector final {
    static_assert(N > 0 && N <= 512, "Window size must be constrained for deterministic stack usage");

public:
    constexpr ShiftDetector(float warning_threshold, float critical_threshold) noexcept
        : warning_th_(warning_threshold), critical_th_(critical_threshold) {}

    [[nodiscard]] std::expected<ShiftMetrics, DetectionError> evaluate(
        std::span<const float> reference_data,
        std::span<const float> current_data
    ) const noexcept {
        if (reference_data.size() != current_data.size() || reference_data.empty()) {
            return std::unexpected(DetectionError::InvalidSize);
        }
        if (reference_data.size() > N) {
            return std::unexpected(DetectionError::BufferOverflow);
        }

        const std::size_t count = reference_data.size();

        std::array<float, N> sorted_ref{};
        std::array<float, N> sorted_cur{};

        std::copy_n(reference_data.data(), count, sorted_ref.begin());
        std::copy_n(current_data.data(), count, sorted_cur.begin());

        std::sort(sorted_ref.begin(), sorted_ref.begin() + count);
        std::sort(sorted_cur.begin(), sorted_cur.begin() + count);

        // 1. Обчислення одновимірної відстані Вассерштейна W1
        float sum_diff = 0.0f;
        for (std::size_t i = 0; i < count; ++i) {
            sum_diff += std::abs(sorted_ref[i] - sorted_cur[i]);
        }
        const float w1 = sum_diff / static_cast<float>(count);

        // 2. Двовибірковий тест Колмогорова-Смірнова
        float d_max = 0.0f;
        std::size_t i = 0;
        std::size_t j = 0;
        const float step = 1.0f / static_cast<float>(count);

        while (i < count && j < count) {
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

        ShiftStatus status = ShiftStatus::Nominal;
        if (w1 >= critical_th_) {
            status = ShiftStatus::Critical;
        } else if (w1 >= warning_th_) {
            status = ShiftStatus::Warning;
        }

        return ShiftMetrics{
            .wasserstein_w1 = w1,
            .ks_statistic   = d_max,
            .status         = status
        };
    }

private:
    float warning_th_;
    float critical_th_;
};

} // namespace embedded_safety
