// iso9613_calc.cpp — Реалізація стандарту ISO 9613-1 мовою C++20
#include <iostream>
#include <cmath>
#include <vector>
#include <span>
#include <iomanip>
#include <expected>
#include <string_view>

namespace acoustics {

struct Environment {
    double temp_c{20.0};       // Температура повітря у °C
    double rh_percent{50.0};   // Відносна вологість у %
    double pressure_kpa{101.325}; // Тиск у кПа
};

enum class CalculationError {
    InvalidFrequency,
    InvalidHumidity,
    InvalidPressure
};

class AtmosphereAbsorption {
public:
    static std::expected<double, CalculationError> 
    calculate_db_per_km(double freq_hz, const Environment& env) noexcept {
        if (freq_hz <= 0.0) {
            return std::unexpected(CalculationError::InvalidFrequency);
        }
        if (env.rh_percent < 0.0 || env.rh_percent > 100.0) {
            return std::unexpected(CalculationError::InvalidHumidity);
        }
        if (env.pressure_kpa <= 0.0) {
            return std::unexpected(CalculationError::InvalidPressure);
        }

        const double T_k = env.temp_c + 273.15;
        constexpr double T0 = 293.15;
        constexpr double T01 = 273.16;

        const double pr = env.pressure_kpa / 101.325;
        const double Tr = T_k / T0;

        // Паровий тиск над водою за ISO 9613-1
        const double exponent = -6.8346 * std::pow(T01 / T_k, 1.261) + 4.6151;
        const double p_sat_pr = std::pow(10.0, exponent);

        // Молярна концентрація водяної пари h
        double h = env.rh_percent * (p_sat_pr / pr);
        if (h < 1e-6) h = 1e-6;

        // Частоти релаксації O2 та N2
        const double fr_O2 = pr * (24.0 + 4.04e4 * h * (0.02 + h) / (0.391 + h));
        const double fr_N2 = pr * std::pow(Tr, -0.5) * 
                             (9.0 + 280.0 * h * std::exp(-4.170 * (std::pow(Tr, -1.0 / 3.0) - 1.0)));

        // Компоненти згасання
        const double alpha_class = 1.84e-11 * (1.0 / pr) * std::sqrt(Tr);
        const double A_O2 = 0.01275 * std::exp(-2239.1 / T_k);
        const double A_N2 = 0.10680 * std::exp(-3352.0 / T_k);

        const double f2 = freq_hz * freq_hz;
        const double alpha_O2 = std::pow(Tr, -2.5) * (A_O2 * fr_O2 / (fr_O2 * fr_O2 + f2));
        const double alpha_N2 = std::pow(Tr, -2.5) * (A_N2 * fr_N2 / (fr_N2 * fr_N2 + f2));

        return 8.686 * f2 * (alpha_class + alpha_O2 + alpha_N2);
    }

    static void compute_spectrum(std::span<const double> frequencies, 
                                 const Environment& env, 
                                 std::span<double> output_db_km) {
        const size_t n = std::min(frequencies.size(), output_db_km.size());
        for (size_t i = 0; i < n; ++i) {
            auto res = calculate_db_per_km(frequencies[i], env);
            output_db_km[i] = res.value_or(0.0);
        }
    }
};

} // namespace acoustics

int main() {
    using namespace acoustics;

    Environment env{.temp_c = 20.0, .rh_percent = 50.0, .pressure_kpa = 101.325};
    const std::vector<double> freqs = {125.0, 500.0, 1000.0, 4000.0, 8000.0, 40000.0};
    std::vector<double> results(freqs.size());

    AtmosphereAbsorption::compute_spectrum(freqs, env, results);

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "Частота (Гц) | Поглинання (дБ/км) | Поглинання (дБ/м)\n";
    std::cout << "--------------------------------------------------\n";
    for (size_t i = 0; i < freqs.size(); ++i) {
        std::cout << std::setw(11) << freqs[i] << " | "
                  << std::setw(17) << results[i] << " | "
                  << std::setw(16) << std::setprecision(5) << (results[i] / 1000.0) << "\n";
        std::cout << std::setprecision(3);
    }

    return 0;
}
