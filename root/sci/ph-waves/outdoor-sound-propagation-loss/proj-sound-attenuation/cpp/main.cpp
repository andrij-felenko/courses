#include <iostream>
#include <cmath>
#include <vector>
#include <optional>
#include <span>
#include <iomanip>

namespace acoustic {

struct Environment {
    double temperature_c{20.0};
    double pressure_kpa{101.325};
    double relative_humidity_pct{50.0};
};

struct AbsorptionResult {
    double alpha_db_m{0.0};
    double alpha_db_km{0.0};
    double fr_oxygen_hz{0.0};
    double fr_nitrogen_hz{0.0};
    double molar_humidity_pct{0.0};
};

class AtmosphericAbsorptionCalculator {
public:
    static constexpr double p_pr = 101.325; // кПа
    static constexpr double T_pr = 293.15;  // К
    static constexpr double T_01 = 273.16;  // К

    [[nodiscard]] static std::optional<AbsorptionResult> 
    calculate(const Environment& env, double frequency_hz) noexcept {
        if (frequency_hz <= 0.0 || env.relative_humidity_pct < 0.0 || env.relative_humidity_pct > 100.0) {
            return std::nullopt;
        }

        const double T_k = env.temperature_c + 273.15;
        if (T_k <= 0.0) return std::nullopt;

        const double p_rel = env.pressure_kpa / p_pr;
        const double T_rel = T_k / T_pr;

        // 1. Молярна концентрація вологи
        const double exp_val = -6.8346 * std::pow(T_01 / T_k, 1.261) + 4.6151;
        const double p_sat_rel = std::pow(10.0, exp_val);
        const double h = env.relative_humidity_pct * (p_sat_rel / p_rel);

        // 2. Частоти релаксації O2 та N2
        const double fr_O = p_rel * (24.0 + 4.04e4 * h * (0.02 + h) / (0.391 + h));
        const double fr_N = p_rel * std::pow(T_rel, -0.5) * 
                            (9.0 + 280.0 * h * std::exp(-4.17 * (std::pow(T_rel, -1.0/3.0) - 1.0)));

        // 3. Складові поглинання
        const double alpha_cl_term = 1.84e-11 * (1.0 / p_rel) * std::sqrt(T_rel);
        const double alpha_O_term  = std::pow(T_rel, -2.5) * 0.1068 * std::exp(-3352.0 / T_k) * 
                                    (fr_O / (fr_O * fr_O + frequency_hz * frequency_hz));
        const double alpha_N_term  = std::pow(T_rel, -2.5) * 0.01275 * std::exp(-2239.1 / T_k) * 
                                    (fr_N / (fr_N * fr_N + frequency_hz * frequency_hz));

        const double f2 = frequency_hz * frequency_hz;
        const double alpha_db_m = 8.686 * f2 * (alpha_cl_term + alpha_O_term + alpha_N_term);

        return AbsorptionResult{
            .alpha_db_m = alpha_db_m,
            .alpha_db_km = alpha_db_m * 1000.0,
            .fr_oxygen_hz = fr_O,
            .fr_nitrogen_hz = fr_N,
            .molar_humidity_pct = h
        };
    }

    [[nodiscard]] static std::vector<double> 
    calculate_spectrum(const Environment& env, std::span<const double> frequencies_hz) {
        std::vector<double> results;
        results.reserve(frequencies_hz.size());
        for (double freq : frequencies_hz) {
            if (auto res = calculate(env, freq)) {
                results.push_back(res->alpha_db_km);
            } else {
                results.push_back(0.0);
            }
        }
        return results;
    }
};

} // namespace acoustic

int main() {
    acoustic::Environment env{.temperature_c = 20.0, .pressure_kpa = 101.325, .relative_humidity_pct = 50.0};
    constexpr double freq = 4000.0;

    if (auto res = acoustic::AtmosphericAbsorptionCalculator::calculate(env, freq)) {
        std::cout << "=== ISO 9613-1 Розрахунок (C++) ===\n"
                  << std::fixed << std::setprecision(2)
                  << "Частота: " << freq << " Гц | T: " << env.temperature_c << " °C | RH: " << env.relative_humidity_pct << " %\n"
                  << "Частота релаксації O2: " << res->fr_oxygen_hz << " Гц\n"
                  << "Частота релаксації N2: " << res->fr_nitrogen_hz << " Гц\n"
                  << std::setprecision(5)
                  << "Коефіцієнт поглинання alpha: " << res->alpha_db_m << " дБ/м (" 
                  << std::setprecision(2) << res->alpha_db_km << " дБ/км)\n";
    }

    const std::vector<double> freqs{100.0, 500.0, 1000.0, 4000.0, 10000.0};
    auto spectrum = acoustic::AtmosphericAbsorptionCalculator::calculate_spectrum(env, freqs);

    std::cout << "\nСпектр поглинання (дБ/км):\n";
    for (size_t i = 0; i < freqs.size(); ++i) {
        std::cout << "  " << std::setw(7) << freqs[i] << " Гц : " << spectrum[i] << " дБ/км\n";
    }

    return 0;
}
