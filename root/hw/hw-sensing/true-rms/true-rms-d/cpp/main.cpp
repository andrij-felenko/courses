#include <cmath>
#include <span>
#include <numeric>
#include <algorithm>

namespace sensing {

// Ідіоматичний C++ True RMS аналізатор на базі std::span
[[nodiscard]] float calculate_true_rms(std::span<const float> samples) noexcept {
    if (samples.empty()) {
        return 0.0f;
    }

    const auto n = samples.size();

    // 1. Паралельне накопичення постійної складової (DC Offset)
    float s_dc0 = 0.0f, s_dc1 = 0.0f, s_dc2 = 0.0f, s_dc3 = 0.0f;
    size_t i = 0;
    for (; i + 3 < n; i += 4) {
        s_dc0 += samples[i + 0];
        s_dc1 += samples[i + 1];
        s_dc2 += samples[i + 2];
        s_dc3 += samples[i + 3];
    }
    float sum_dc = (s_dc0 + s_dc1) + (s_dc2 + s_dc3);
    for (; i < n; ++i) {
        sum_dc += samples[i];
    }
    const float dc_offset = sum_dc / static_cast<float>(n);

    // 2. Накопичення квадратів змінної частини
    float s_sq0 = 0.0f, s_sq1 = 0.0f, s_sq2 = 0.0f, s_sq3 = 0.0f;
    i = 0;
    for (; i + 3 < n; i += 4) {
        const float d0 = samples[i + 0] - dc_offset;
        const float d1 = samples[i + 1] - dc_offset;
        const float d2 = samples[i + 2] - dc_offset;
        const float d3 = samples[i + 3] - dc_offset;

        s_sq0 += d0 * d0;
        s_sq1 += d1 * d1;
        s_sq2 += d2 * d2;
        s_sq3 += d3 * d3;
    }
    float total_sq = (s_sq0 + s_sq1) + (s_sq2 + s_sq3);
    for (; i < n; ++i) {
        const float d = samples[i] - dc_offset;
        total_sq += d * d;
    }

    return std::sqrt(total_sq / static_cast<float>(n));
}

} // namespace sensing
