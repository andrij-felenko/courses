#include <cstdint>
#include <cmath>
#include <chrono>
#include <optional>
#include <span>
#include <string_view>

namespace metrology {

constexpr uint32_t MagicWord = 0x54524143U; // "TRAC"

struct CalibrationProfile {
    uint32_t magic{MagicWord};
    std::chrono::sys_seconds cal_time{};
    std::chrono::seconds validity_period{};
    float temp_cal_celsius{23.0f};
    float gain_slope{1.0f};
    float offset_zero{0.0f};
    float u_std_volts{1.0e-4f};
    float tc_ppm_celsius{5.0f};
    float drift_ppm_year{10.0f};
    uint32_t crc32{0};
};

struct Measurement {
    double value_volts{0.0};
    double expanded_uncertainty{0.0};
    bool is_expired{false};

    [[nodiscard]] constexpr double min_bound() const noexcept {
        return value_volts - expanded_uncertainty;
    }

    [[nodiscard]] constexpr double max_bound() const noexcept {
        return value_volts + expanded_uncertainty;
    }
};

class MetrologyEngine {
public:
    explicit MetrologyEngine(const CalibrationProfile& profile) noexcept
        : profile_(profile), valid_(validate_profile(profile)) {}

    [[nodiscard]] bool is_valid() const noexcept { return valid_; }

    [[nodiscard]] std::optional<Measurement> process(
        float raw_volts,
        float current_temp,
        std::chrono::sys_seconds current_time) const noexcept 
    {
        if (!valid_) {
            return std::nullopt;
        }

        const auto elapsed = (current_time >= profile_.cal_time)
                                 ? (current_time - profile_.cal_time)
                                 : std::chrono::seconds{0};

        const bool expired = (elapsed > profile_.validity_period);

        // 1. Корекція функції відгуку
        const double corrected = (static_cast<double>(raw_volts) - profile_.offset_zero) 
                                * profile_.gain_slope;

        // 2. Бюджет невизначеностей
        const double u_std = profile_.u_std_volts;

        const double years = std::chrono::duration<double, std::ratio<31557600>>(elapsed).count();
        const double u_aging = std::abs(corrected) * (profile_.drift_ppm_year * years * 1e-6);

        const double delta_temp = std::abs(current_temp - profile_.temp_cal_celsius);
        const double u_temp = (std::abs(corrected) * (profile_.tc_ppm_celsius * delta_temp * 1e-6)) 
                             / std::sqrt(3.0);

        constexpr double u_noise = 2.0e-5; // 20 мкВ

        // 3. Сумарна невизначеність
        const double u_combined = std::sqrt(u_std * u_std + 
                                            u_aging * u_aging + 
                                            u_temp * u_temp + 
                                            u_noise * u_noise);

        constexpr double coverage_factor_k = 2.0; // 95.45% рівень довіри
        const double expanded_u = u_combined * coverage_factor_k;

        return Measurement{
            .value_volts = corrected,
            .expanded_uncertainty = expanded_u,
            .is_expired = expired
        };
    }

private:
    CalibrationProfile profile_;
    bool valid_{false};

    static bool validate_profile(const CalibrationProfile& p) noexcept {
        if (p.magic != MagicWord) return false;
        
        auto bytes = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(&p),
            sizeof(CalibrationProfile) - sizeof(uint32_t)
        );

        uint32_t crc = 0xFFFFFFFFU;
        for (uint8_t b : bytes) {
            crc ^= b;
            for (int i = 0; i < 8; ++i) {
                crc = (crc >> 1) ^ (0xEDB88320U & (-(static_cast<int32_t>(crc & 1))));
            }
        }
        return p.crc32 == (~crc);
    }
};

} // namespace metrology
