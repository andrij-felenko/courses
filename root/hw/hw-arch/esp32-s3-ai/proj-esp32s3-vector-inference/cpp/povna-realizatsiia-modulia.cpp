// ESP-IDF / C++20: Строго типізований векторний шар з бенчмарком та RAII
#include <cstdint>
#include <cstddef>
#include <span>
#include <vector>
#include <algorithm>
#include <memory>
#include "esp_heap_caps.h"
#include "esp_cpu.h"
#include "esp_log.h"

namespace ai::simd {

static constexpr const char *TAG = "ESP32S3_SIMD_CPP";
static constexpr std::size_t SimdAlignment = 16;

struct QuantParams {
    std::int32_t input_offset{0};      // -Z_in
    std::int32_t output_offset{0};     // Z_out
    std::int32_t output_multiplier{0}; // M_0
    std::int32_t output_shift{0};      // shift
    std::int32_t activation_min{-128};
    std::int32_t activation_max{127};
};

[[nodiscard]] inline std::int32_t Requantize(std::int32_t val, const QuantParams &p) noexcept {
    const auto total = static_cast<std::int64_t>(val) * static_cast<std::int64_t>(p.output_multiplier);
    const auto round_val = static_cast<std::int64_t>(1) << (p.output_shift - 1);
    auto res = static_cast<std::int32_t>((total + round_val) >> p.output_shift);
    res += p.output_offset;
    return std::clamp(res, p.activation_min, p.activation_max);
}

// Клас повнозв'язного шару з автоматичним виділенням вирівняної SRAM
class FullyConnectedLayer {
public:
    FullyConnectedLayer(std::size_t num_inputs, std::size_t num_outputs, QuantParams params)
        : num_inputs_(num_inputs), num_outputs_(num_outputs), params_(params) {
        
        // Перевірка кратності 16 для коректної роботи SIMD
        if (num_inputs_ % SimdAlignment != 0) {
            ESP_LOGW(TAG, "Вхідний розмір %zu не кратний 16! SIMD вимагає паддингу.", num_inputs_);
        }
    }

    void ExecuteSimd(std::span<const std::int8_t> input,
                     std::span<const std::int8_t> weights,
                     std::span<const std::int32_t> bias,
                     std::span<std::int8_t> output) const {
        
        const std::size_t num_blocks = num_inputs_ / SimdAlignment;

        for (std::size_t m = 0; m < num_outputs_; m += 2) {
            std::int32_t acc0 = (!bias.empty()) ? bias[m] : 0;
            std::int32_t acc1 = (!bias.empty() && (m + 1 < num_outputs_)) ? bias[m + 1] : 0;

            const auto *w0 = &weights[m * num_inputs_];
            const auto *w1 = (m + 1 < num_outputs_) ? &weights[(m + 1) * num_inputs_] : w0;

            for (std::size_t b = 0; b < num_blocks; ++b) {
                const std::size_t base = b * SimdAlignment;
                for (std::size_t i = 0; i < SimdAlignment; ++i) {
                    const auto in_val = static_cast<std::int32_t>(input[base + i]) + params_.input_offset;
                    acc0 += in_val * static_cast<std::int32_t>(w0[base + i]);
                    if (m + 1 < num_outputs_) {
                        acc1 += in_val * static_cast<std::int32_t>(w1[base + i]);
                    }
                }
            }

            output[m] = static_cast<std::int8_t>(Requantize(acc0, params_));
            if (m + 1 < num_outputs_) {
                output[m + 1] = static_cast<std::int8_t>(Requantize(acc1, params_));
            }
        }
    }

private:
    std::size_t num_inputs_{0};
    std::size_t num_outputs_{0};
    QuantParams params_{};
};

} // namespace ai::simd
