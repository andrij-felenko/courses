// kelvin_meter.cpp — Прецизійний 4-провідний вимірювач опору (C++20 / Modern C++)
#include <cstdint>
#include <cmath>
#include <expected>
#include <span>

namespace kelvin {

enum class Status {
    Ok,
    InvalidConfig,
    AdcOverflow,
    SensorOpenCircuit
};

struct Config {
    float r_ref_ohm{1000.0f};           // Опорний резистор R_ref = 1 кОм
    float excitation_current_a{0.001f}; // Струм збудження 1 мА
    std::int32_t adc_max_code{8388607}; // 2^23 - 1
    float pga_gain{16.0f};              // Підсилення PGA
    bool ratiometric{true};             // Ратіометричний режим
};

struct Result {
    float resistance_ohm;
    float temperature_c;
    float thermal_emf_v;
};

class MicroOhmmeter {
public:
    constexpr explicit MicroOhmmeter(Config config) noexcept : cfg_(config) {}

    [[nodiscard]] std::expected<Result, Status>
    process_samples(std::int32_t raw_pos, std::int32_t raw_neg) const noexcept {
        if (cfg_.r_ref_ohm <= 0.0f || cfg_.pga_gain <= 0.0f || cfg_.adc_max_code <= 0) {
            return std::unexpected(Status::InvalidConfig);
        }

        if (std::abs(raw_pos) >= cfg_.adc_max_code || std::abs(raw_neg) >= cfg_.adc_max_code) {
            return std::unexpected(Status::AdcOverflow);
        }

        const float delta_code = static_cast<float>(raw_pos - raw_neg) * 0.5f;
        const float sum_code   = static_cast<float>(raw_pos + raw_neg) * 0.5f;

        const float r_x = cfg_.r_ref_ohm * (delta_code / (static_cast<float>(cfg_.adc_max_code) * cfg_.pga_gain));

        if (r_x > cfg_.r_ref_ohm * 10.0f) {
            return std::unexpected(Status::SensorOpenCircuit);
        }

        const float v_lsb = (cfg_.excitation_current_a * cfg_.r_ref_ohm) / static_cast<float>(cfg_.adc_max_code);
        const float v_emf = sum_code * v_lsb / cfg_.pga_gain;

        return Result{
            .resistance_ohm = r_x,
            .temperature_c  = calculate_pt100_temp(r_x),
            .thermal_emf_v  = v_emf
        };
    }

private:
    Config cfg_;

    [[nodiscard]] static constexpr float calculate_pt100_temp(float r_ohm) noexcept {
        constexpr float R0 = 100.0f;
        constexpr float A = 3.9083e-3f;
        constexpr float B = -5.775e-7f;

        if (r_ohm >= R0) {
            float disc = A * A - 4.0f * B * (1.0f - r_ohm / R0);
            if (disc < 0.0f) return -999.0f;
            return (-A + std::sqrt(disc)) / (2.0f * B);
        }
        return (r_ohm - R0) / (R0 * A);
    }
};

} // namespace kelvin
