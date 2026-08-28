#include <cstdint>
#include <cmath>
#include <array>
#include <expected>
#include <numbers>

namespace rf {

enum class SynthError {
    InvalidFrequency,
    InvalidReference,
    SpiFailure
};

class IntegratedSynthesizer {
public:
    static constexpr double MIN_FREQ_HZ = 35.0e6;
    static constexpr double MAX_FREQ_HZ = 4400.0e6;

    struct RegisterMap {
        std::array<uint32_t, 6> raw_registers{};
        double calculated_freq_hz{0.0};
    };

    explicit IntegratedSynthesizer(double ref_osc_hz = 25.0e6) noexcept
        : ref_osc_hz_(ref_osc_hz) {}

    [[nodiscard]] std::expected<RegisterMap, SynthError> prepare_registers(double target_freq_hz) const noexcept {
        if (target_freq_hz < MIN_FREQ_HZ || target_freq_hz > MAX_FREQ_HZ) {
            return std::unexpected(SynthError::InvalidFrequency);
        }
        if (ref_osc_hz_ <= 0.0) {
            return std::unexpected(SynthError::InvalidReference);
        }

        RegisterMap map{};
        uint32_t rf_div = 1;
        uint32_t rf_div_select = 0;
        double vco_freq = target_freq_hz;

        while (vco_freq < 2200.0e6 && rf_div_select < 6) {
            vco_freq *= 2.0;
            rf_div *= 2;
            rf_div_select++;
        }

        constexpr uint32_t r_div = 1;
        constexpr uint32_t mod = 4000;
        const double f_pfd = ref_osc_hz_ / r_div;

        const double n_total = vco_freq / f_pfd;
        auto integer_part = static_cast<uint32_t>(std::floor(n_total));
        auto frac_part = static_cast<uint32_t>(std::round((n_total - integer_part) * mod));

        if (frac_part >= mod) {
            integer_part++;
            frac_part = 0;
        }

        map.calculated_freq_hz = (static_cast<double>(integer_part) +
                                 (static_cast<double>(frac_part) / mod)) * f_pfd / rf_div;

        map.raw_registers[0] = (integer_part << 15) | (frac_part << 3) | 0u;
        map.raw_registers[1] = (1u << 27) | (mod << 3) | 1u;
        map.raw_registers[2] = (7u << 9) | (r_div << 3) | (1u << 6) | 2u;
        map.raw_registers[3] = (1u << 15) | (100u << 3) | 3u;
        map.raw_registers[4] = (rf_div_select << 20) | (1u << 5) | (3u << 3) | 4u;
        map.raw_registers[5] = (1u << 22) | (3u << 16) | 5u;

        return map;
    }

private:
    double ref_osc_hz_;
};

} // namespace rf
