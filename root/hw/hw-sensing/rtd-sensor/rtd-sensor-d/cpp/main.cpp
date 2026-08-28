#include <cmath>
#include <concepts>
#include <cstdint>
#include <expected>
#include <limits>

namespace sensing {

enum class RtdModel : uint8_t {
    Pt100,
    Pt1000
};

enum class RtdError : uint8_t {
    OpenCircuit,   // Обрив лінії чи сенсора
    ShortCircuit,  // Коротке замикання
    OutOfRange,    // Вихід за межі стандарту (-200..+850 °C)
    InvalidParameter
};

struct RtdMeasurement {
    float resistance_ohm;
    float temperature_celsius;
};

// Константи стандарту IEC 60751
namespace constants {
    constexpr float CvdA = 3.90830e-3f;
    constexpr float CvdB = -5.77500e-7f;
    constexpr float CvdC = -4.18300e-12f;
}

template <RtdModel Model = RtdModel::Pt100>
class PlatinumRtdDriver {
public:
    static constexpr float NominalR0 = (Model == RtdModel::Pt1000) ? 1000.0f : 100.0f;
    static constexpr float MinValidResistance = (Model == RtdModel::Pt1000) ? 150.0f : 15.0f;
    static constexpr float MaxValidResistance = (Model == RtdModel::Pt1000) ? 4100.0f : 410.0f;

    struct Config {
        float reference_resistor_ohm{Model == RtdModel::Pt1000 ? 40000.0f : 4000.0f};
        uint32_t adc_full_scale_code{8388607}; // 2^23 - 1 (24-біт знаковий)
        float pga_gain{1.0f};
        float calibrated_r0{NominalR0};
    };

    explicit constexpr PlatinumRtdDriver(const Config& config) noexcept : config_(config) {}

    [[nodiscard]] constexpr float r0() const noexcept { return config_.calibrated_r0; }

    /**
     * @brief Перетворення виміряного опору в температуру за рівнянням Каллендара-Ван Дюзена
     */
    [[nodiscard]] std::expected<float, RtdError> resistanceToTemperature(float resistance) const noexcept {
        if (resistance < MinValidResistance) {
            return std::unexpected(RtdError::ShortCircuit);
        }
        if (resistance > MaxValidResistance) {
            return std::unexpected(RtdError::OpenCircuit);
        }

        const float r_norm = resistance / config_.calibrated_r0;

        if (resistance >= config_.calibrated_r0) {
            // T >= 0 °C: точний аналітичний розв'язок
            const float discriminant = (constants::CvdA * constants::CvdA) - 
                                       4.0f * constants::CvdB * (1.0f - r_norm);
            if (discriminant < 0.0f) {
                return std::unexpected(RtdError::OutOfRange);
            }
            return (-constants::CvdA + std::sqrt(discriminant)) / (2.0f * constants::CvdB);
        } else {
            // T < 0 °C: числове розв'язання методом Ньютона-Рафсона
            float t = (r_norm - 1.0f) / constants::CvdA;
            
            for (size_t iter = 0; iter < 4; ++iter) {
                const float t2 = t * t;
                const float t3 = t2 * t;
                const float t4 = t3 * t;

                const float f = config_.calibrated_r0 * (1.0f + constants::CvdA * t + 
                                constants::CvdB * t2 - 100.0f * constants::CvdC * t3 + 
                                constants::CvdC * t4) - resistance;

                const float f_prime = config_.calibrated_r0 * (constants::CvdA + 
                                      2.0f * constants::CvdB * t - 
                                      300.0f * constants::CvdC * t2 + 
                                      4.0f * constants::CvdC * t3);

                if (std::abs(f_prime) < 1e-7f) {
                    break;
                }

                const float delta = f / f_prime;
                t -= delta;

                if (std::abs(delta) < 1e-4f) {
                    break;
                }
            }
            return t;
        }
    }

    /**
     * @brief Повна раціометрична обробка відліку АЦП
     */
    [[nodiscard]] std::expected<RtdMeasurement, RtdError> processAdcCode(int32_t raw_code) const noexcept {
        if (config_.adc_full_scale_code == 0 || config_.pga_gain <= 0.0f || raw_code < 0) {
            return std::unexpected(RtdError::InvalidParameter);
        }

        const float measured_r = (static_cast<float>(raw_code) / static_cast<float>(config_.adc_full_scale_code)) *
                                 (config_.reference_resistor_ohm / config_.pga_gain);

        auto temp_res = resistanceToTemperature(measured_r);
        if (!temp_res) {
            return std::unexpected(temp_res.error());
        }

        return RtdMeasurement{
            .resistance_ohm = measured_r,
            .temperature_celsius = *temp_res
        };
    }

private:
    Config config_;
};

} // namespace sensing
