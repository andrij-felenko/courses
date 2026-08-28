#include <cstdint>
#include <cmath>
#include <expected>
#include <system_error>

enum class BaudCalcError {
    InvalidParameters,
    PrescalerOutOfRange,
    ToleranceExceeded
};

struct BaudConfig {
    uint32_t brr_register{0};
    uint32_t actual_baud{0};
    float error_percent{0.0f};
    uint8_t oversampling{16};
};

class BaudRateCalculator {
public:
    static constexpr float MaxTolerancePercent = 2.5f;

    /**
     * @brief Обчислює конфігурацію BRR із суворою перевіркою типом C++23 std::expected
     */
    [[nodiscard]] static std::expected<BaudConfig, BaudCalcError> calculate(
        uint32_t pclk_hz, 
        uint32_t target_baud, 
        bool allow_oversample8 = false) noexcept 
    {
        if (pclk_hz == 0 || target_baud == 0) {
            return std::unexpected(BaudCalcError::InvalidParameters);
        }

        BaudConfig best_config{};
        float min_error = 100.0f;
        bool found = false;

        const uint8_t min_os = allow_oversample8 ? 8 : 16;

        for (uint8_t os = 16; os >= min_os; os -= 8) {
            const float usartdiv = static_cast<float>(pclk_hz) / static_cast<float>(os * target_baud);
            
            auto mantissa = static_cast<uint32_t>(std::floor(usartdiv));
            const float fraction_part = usartdiv - static_cast<float>(mantissa);
            const float frac_scale = static_cast<float>(os);
            auto fraction = static_cast<uint32_t>(std::round(fraction_part * frac_scale));

            if (fraction >= os) {
                fraction = 0;
                mantissa += 1;
            }

            if (mantissa == 0 || mantissa > 0xFFFF) {
                continue;
            }

            uint32_t brr = 0;
            if (os == 16) {
                brr = (mantissa << 4) | (fraction & 0x0F);
            } else {
                brr = (mantissa << 4) | (fraction & 0x07);
            }

            const float div_actual = static_cast<float>(mantissa) + (static_cast<float>(fraction) / static_cast<float>(os));
            const auto actual_baud = static_cast<uint32_t>(std::round(static_cast<float>(pclk_hz) / (static_cast<float>(os) * div_actual)));

            const float diff = static_cast<float>(actual_baud) - static_cast<float>(target_baud);
            const float error_pct = std::abs((diff / static_cast<float>(target_baud)) * 100.0f);

            if (error_pct < min_error) {
                min_error = error_pct;
                best_config = BaudConfig{
                    .brr_register = brr,
                    .actual_baud = actual_baud,
                    .error_percent = error_pct,
                    .oversampling = os
                };
                found = true;
            }

            if (min_error <= MaxTolerancePercent) {
                break;
            }
        }

        if (!found) {
            return std::unexpected(BaudCalcError::PrescalerOutOfRange);
        }

        if (best_config.error_percent > MaxTolerancePercent) {
            return std::unexpected(BaudCalcError::ToleranceExceeded);
        }

        return best_config;
    }
};
