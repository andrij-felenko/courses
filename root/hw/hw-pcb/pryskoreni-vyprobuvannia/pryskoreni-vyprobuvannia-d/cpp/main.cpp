#include <iostream>
#include <iomanip>
#include <cmath>
#include <numbers>
#include <expected>
#include <string_view>

namespace reliability {

inline constexpr double kb_ev = 8.617333e-5; // Константа Больцмана (еВ/К)

enum class ModelError {
    invalid_temperature,
    invalid_frequency,
    invalid_humidity,
    zero_division
};

struct ArrheniusConfig {
    double temp_use_c{45.0};
    double temp_stress_c{125.0};
    double activation_energy_ev{0.70};

    [[nodiscard]] constexpr double kelvin_use() const noexcept { return temp_use_c + 273.15; }
    [[nodiscard]] constexpr double kelvin_stress() const noexcept { return temp_stress_c + 273.15; }
};

struct NorrisLandzbergConfig {
    double delta_t_use_c{40.0};
    double delta_t_stress_c{165.0};
    double freq_use_cycles_per_day{3.0};
    double freq_stress_cycles_per_hour{1.0};
    double t_max_use_c{50.0};
    double t_max_stress_c{125.0};
    double m_fatigue_exponent{2.65};    // Для безсвинцевого SAC305
    double n_frequency_exponent{0.33};  // Показник повзучості
    double activation_energy_ev{0.122}; // Енергія релаксації Sn

    [[nodiscard]] constexpr double kelvin_max_use() const noexcept { return t_max_use_c + 273.15; }
    [[nodiscard]] constexpr double kelvin_max_stress() const noexcept { return t_max_stress_c + 273.15; }
};

struct PeckConfig {
    double rh_use_percent{60.0};
    double rh_stress_percent{85.0};
    double temp_use_c{40.0};
    double temp_stress_c{130.0};
    double humidity_exponent{2.7};
    double activation_energy_ev{0.80};

    [[nodiscard]] constexpr double kelvin_use() const noexcept { return temp_use_c + 273.15; }
    [[nodiscard]] constexpr double kelvin_stress() const noexcept { return temp_stress_c + 273.15; }
};

class AcceleratedTestCalculator {
public:
    [[nodiscard]] static std::expected<double, ModelError> 
    calculate_arrhenius_af(const ArrheniusConfig& cfg) noexcept {
        if (cfg.kelvin_use() <= 0.0 || cfg.kelvin_stress() <= 0.0) {
            return std::unexpected(ModelError::invalid_temperature);
        }
        const double diff = (1.0 / cfg.kelvin_use()) - (1.0 / cfg.kelvin_stress());
        return std::exp((cfg.activation_energy_ev / kb_ev) * diff);
    }

    [[nodiscard]] static std::expected<double, ModelError> 
    calculate_norris_landzberg_af(const NorrisLandzbergConfig& cfg) noexcept {
        if (cfg.delta_t_use_c <= 0.0 || cfg.freq_use_cycles_per_day <= 0.0 || cfg.freq_stress_cycles_per_hour <= 0.0) {
            return std::unexpected(ModelError::invalid_frequency);
        }
        const double freq_stress_cpd = cfg.freq_stress_cycles_per_hour * 24.0;
        
        const double term_dt = std::pow(cfg.delta_t_stress_c / cfg.delta_t_use_c, cfg.m_fatigue_exponent);
        const double term_freq = std::pow(cfg.freq_use_cycles_per_day / freq_stress_cpd, cfg.n_frequency_exponent);
        const double temp_diff = (1.0 / cfg.kelvin_max_use()) - (1.0 / cfg.kelvin_max_stress());
        const double term_temp = std::exp((cfg.activation_energy_ev / kb_ev) * temp_diff);

        return term_dt * term_freq * term_temp;
    }

    [[nodiscard]] static std::expected<double, ModelError> 
    calculate_peck_af(const PeckConfig& cfg) noexcept {
        if (cfg.rh_use_percent <= 0.0 || cfg.rh_stress_percent <= 0.0) {
            return std::unexpected(ModelError::invalid_humidity);
        }
        const double term_rh = std::pow(cfg.rh_stress_percent / cfg.rh_use_percent, cfg.humidity_exponent);
        const double temp_diff = (1.0 / cfg.kelvin_use()) - (1.0 / cfg.kelvin_stress());
        const double term_temp = std::exp((cfg.activation_energy_ev / kb_ev) * temp_diff);

        return term_rh * term_temp;
    }
};

} // namespace reliability

int main() {
    using namespace reliability;

    std::cout << "=== Інженерний калькулятор прискорених випробувань (C++23) ===\n\n";

    // 1. Модель Арреніуса
    const ArrheniusConfig arr_cfg{.temp_use_c = 45.0, .temp_stress_c = 125.0, .activation_energy_ev = 0.70};
    if (auto af_arr = AcceleratedTestCalculator::calculate_arrhenius_af(arr_cfg); af_arr.has_value()) {
        const double field_hours = 87600.0; // 10 років
        const double test_hours = field_hours / *af_arr;
        std::cout << "[1] Термічне старіння (Arrhenius):\n"
                  << "    Коефіцієнт прискорення AF: " << std::fixed << std::setprecision(2) << *af_arr << "\n"
                  << "    Еквівалент 10 років (87600 год): " << std::setprecision(1) << test_hours 
                  << " год (" << (test_hours / 24.0) << " діб при 125 °C)\n\n";
    }

    // 2. Модель Норріса-Ландзберга
    const NorrisLandzbergConfig nl_cfg{
        .delta_t_use_c = 40.0,
        .delta_t_stress_c = 165.0,
        .freq_use_cycles_per_day = 3.0,
        .freq_stress_cycles_per_hour = 1.0,
        .t_max_use_c = 50.0,
        .t_max_stress_c = 125.0,
        .m_fatigue_exponent = 2.65,
        .n_frequency_exponent = 0.33,
        .activation_energy_ev = 0.122
    };
    if (auto af_nl = AcceleratedTestCalculator::calculate_norris_landzberg_af(nl_cfg); af_nl.has_value()) {
        const double field_cycles = 10.0 * 365.0 * 3.0; // 10950 циклів
        const double test_cycles = field_cycles / *af_nl;
        std::cout << "[2] Термомеханічна втома пайки (Norris-Landzberg SAC305):\n"
                  << "    Коефіцієнт прискорення AF: " << *af_nl << "\n"
                  << "    Еквівалент 10 років (" << static_cast<int>(field_cycles) << " циклів): " 
                  << std::ceil(test_cycles) << " циклів у камері (" << (test_cycles / 24.0) << " діб)\n\n";
    }

    // 3. Модель Пека (HAST)
    const PeckConfig peck_cfg{
        .rh_use_percent = 60.0,
        .rh_stress_percent = 85.0,
        .temp_use_c = 40.0,
        .temp_stress_c = 130.0,
        .humidity_exponent = 2.7,
        .activation_energy_ev = 0.80
    };
    if (auto af_peck = AcceleratedTestCalculator::calculate_peck_af(peck_cfg); af_peck.has_value()) {
        const double field_hours = 87600.0;
        const double test_hours = field_hours / *af_peck;
        std::cout << "[3] Кліматична деградація та вологість (Peck HAST):\n"
                  << "    Коефіцієнт прискорення AF: " << *af_peck << "\n"
                  << "    Еквівалент 10 років вологи: " << test_hours << " год в автоклаві HAST\n";
    }

    return 0;
}
