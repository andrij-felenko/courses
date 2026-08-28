// C++ Implementation
#include <iostream>
#include <numeric>
#include <optional>
#include <cstdint>

class LocalOscillatorPLL {
public:
    struct Config {
        std::uint32_t ref_freq_hz{26'000'000};  // 26 MHz TCXO
        std::uint32_t vco_min_hz{2'200'000'000}; // 2.2 GHz
        std::uint32_t vco_max_hz{4'400'000'000}; // 4.4 GHz
    };

    struct Settings {
        std::uint32_t int_val;
        std::uint32_t frac_val;
        std::uint32_t mod_val;
        std::uint32_t rf_div;
        std::uint32_t actual_hz;
    };

    explicit LocalOscillatorPLL(Config cfg) : config_(cfg) {}

    [[nodiscard]] std::optional<Settings> calculate(std::uint32_t target_lo_hz) const {
        if (target_lo_hz == 0) return std::nullopt;

        std::uint32_t rf_div = 1;
        std::uint64_t vco_freq = target_lo_hz;

        while (vco_freq < config_.vco_min_hz && rf_div <= 64) {
            rf_div *= 2;
            vco_freq = static_cast<std::uint64_t>(target_lo_hz) * rf_div;
        }

        if (vco_freq > config_.vco_max_hz) {
            return std::nullopt;
        }

        const std::uint64_t pfd_freq = config_.ref_freq_hz;
        const auto int_part = static_cast<std::uint32_t>(vco_freq / pfd_freq);
        const std::uint64_t remainder = vco_freq % pfd_freq;

        constexpr std::uint32_t max_modulus = 4095;
        std::uint64_t frac_part = (remainder * max_modulus) / pfd_freq;
        std::uint32_t mod_part = max_modulus;

        if (frac_part > 0) {
            const auto g = std::gcd(frac_part, static_cast<std::uint64_t>(mod_part));
            frac_part /= g;
            mod_part /= static_cast<std::uint32_t>(g);
        } else {
            mod_part = 1;
        }

        const std::uint64_t calc_vco = int_part * pfd_freq + (pfd_freq * frac_part) / mod_part;
        const auto actual_lo = static_cast<std::uint32_t>(calc_vco / rf_div);

        return Settings{
            .int_val = int_part,
            .frac_val = static_cast<std::uint32_t>(frac_part),
            .mod_val = mod_part,
            .rf_div = rf_div,
            .actual_hz = actual_lo
        };
    }

private:
    Config config_;
};

int main() {
    LocalOscillatorPLL pll({.ref_freq_hz = 26'000'000});
    constexpr std::uint32_t target = 433'920'000; // 433.92 MHz

    if (const auto settings = pll.calculate(target)) {
        std::cout << "Target LO: " << target << " Hz\n"
                  << "Actual LO: " << settings->actual_hz << " Hz\n"
                  << "RF_DIV=" << settings->rf_div
                  << ", INT=" << settings->int_val
                  << ", FRAC=" << settings->frac_val
                  << ", MOD=" << settings->mod_val << '\n';
    } else {
        std::cerr << "Error: Frequency cannot be synthesised!\n";
    }
    return 0;
}
