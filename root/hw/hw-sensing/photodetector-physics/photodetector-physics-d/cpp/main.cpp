#include <iostream>
#include <cmath>
#include <numbers>
#include <expected>
#include <string_view>
#include <iomanip>

namespace opto {

inline constexpr double q_elem   = 1.602176634e-19; /* Кулон */
inline constexpr double h_planck = 6.62607015e-34;  /* Дж * с */
inline constexpr double c_light  = 2.99792458e8;    /* м / с */
inline constexpr double k_boltz  = 1.380649e-23;    /* Дж / К */
inline constexpr double eps_0    = 8.8541878128e-12;/* Ф / м */

struct PhotodiodeConfig {
    double wavelength_m{850.0e-9};
    double quantum_efficiency{0.82};
    double area_m2{0.2e-6};
    double eps_relative{11.7};
    double v_bi{0.7};
    double v_reverse{10.0};
    double n_doping_m3{5.0e20};
    double v_saturation_m_s{1.0e5};
    double r_series_ohm{12.0};
    double r_load_ohm{50.0};
    double r_shunt_ohm{2.0e9};
    double dark_current_a{0.8e-9};
    double temperature_k{300.0};
};

struct PhotodiodeMetrics {
    double responsivity_a_w;
    double depletion_width_m;
    double junction_capacitance_f;
    double f_rc_hz;
    double f_transit_hz;
    double f_cutoff_3db_hz;
    double noise_current_density_a_rthz;
    double nep_w_rthz;
};

enum class CalculationError {
    InvalidWavelength,
    InvalidQuantumEfficiency,
    InvalidGeometryOrDoping,
    ZeroResponsivity
};

[[nodiscard]] constexpr std::string_view to_string(CalculationError err) noexcept {
    switch (err) {
        case CalculationError::InvalidWavelength: return "Довжина хвилі повинна бути > 0";
        case CalculationError::InvalidQuantumEfficiency: return "Квантова ефективність повинна належати (0, 1]";
        case CalculationError::InvalidGeometryOrDoping: return "Площа, концентрація та швидкість мають бути > 0";
        case CalculationError::ZeroResponsivity: return "Розрахункова чутливість дорівнює нулю";
    }
    return "Невідома помилка";
}

[[nodiscard]] std::expected<PhotodiodeMetrics, CalculationError> 
analyze_photodiode(const PhotodiodeConfig& cfg) noexcept {
    if (cfg.wavelength_m <= 0.0) {
        return std::unexpected(CalculationError::InvalidWavelength);
    }
    if (cfg.quantum_efficiency <= 0.0 || cfg.quantum_efficiency > 1.0) {
        return std::unexpected(CalculationError::InvalidQuantumEfficiency);
    }
    if (cfg.area_m2 <= 0.0 || cfg.n_doping_m3 <= 0.0 || cfg.v_saturation_m_s <= 0.0) {
        return std::unexpected(CalculationError::InvalidGeometryOrDoping);
    }

    PhotodiodeMetrics m{};

    /* Спектральна чутливість R(lambda) = (eta * q * lambda) / (h * c) */
    m.responsivity_a_w = (cfg.quantum_efficiency * q_elem * cfg.wavelength_m) / (h_planck * c_light);
    if (m.responsivity_a_w <= 0.0) {
        return std::unexpected(CalculationError::ZeroResponsivity);
    }

    /* Ширина збідненої області W */
    const double v_total = std::max(0.0, cfg.v_bi + cfg.v_reverse);
    const double eps_mat = eps_0 * cfg.eps_relative;
    m.depletion_width_m  = std::sqrt((2.0 * eps_mat * v_total) / (q_elem * cfg.n_doping_m3));

    /* Бар'єрна ємність C_j */
    m.junction_capacitance_f = (m.depletion_width_m > 0.0) ? (eps_mat * cfg.area_m2 / m.depletion_width_m) : 0.0;

    /* RC-зріз */
    const double r_tot = cfg.r_series_ohm + cfg.r_load_ohm;
    m.f_rc_hz = (r_tot > 0.0 && m.junction_capacitance_f > 0.0) 
        ? (1.0 / (2.0 * std::numbers::pi * r_tot * m.junction_capacitance_f)) : 0.0;

    /* Пролітний зріз */
    m.f_transit_hz = (m.depletion_width_m > 0.0) 
        ? (0.443 * cfg.v_saturation_m_s / m.depletion_width_m) : 0.0;

    /* Комбінований зріз -3 дБ */
    if (m.f_rc_hz > 0.0 && m.f_transit_hz > 0.0) {
        const double inv_sq = (1.0 / (m.f_rc_hz * m.f_rc_hz)) + (1.0 / (m.f_transit_hz * m.f_transit_hz));
        m.f_cutoff_3db_hz = 1.0 / std::sqrt(inv_sq);
    }

    /* Шумовий струм і NEP */
    const double shot_noise_sq = 2.0 * q_elem * cfg.dark_current_a;
    const double thermal_noise_sq = (cfg.r_shunt_ohm > 0.0) 
        ? (4.0 * k_boltz * cfg.temperature_k / cfg.r_shunt_ohm) : 0.0;

    m.noise_current_density_a_rthz = std::sqrt(shot_noise_sq + thermal_noise_sq);
    m.nep_w_rthz = m.noise_current_density_a_rthz / m.responsivity_a_w;

    return m;
}

} // namespace opto

int main() {
    const opto::PhotodiodeConfig config{};
    const auto result = opto::analyze_photodiode(config);

    if (!result) {
        std::cerr << "Помилка аналізу: " << opto::to_string(result.error()) << '\n';
        return 1;
    }

    const auto& res = *result;
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "=== Оптоелектронні параметри фотоприймача ===\n";
    std::cout << "Спектральна чутливість R:     " << res.responsivity_a_w << " А/Вт\n";
    std::cout << "Товщина збідненої зони W:    " << res.depletion_width_m * 1e6 << " мкм\n";
    std::cout << "Ємність переходу C_j:        " << res.junction_capacitance_f * 1e12 << " пФ\n";
    std::cout << "RC-смуга (f_RC):             " << res.f_rc_hz * 1e-6 << " МГц\n";
    std::cout << "Дрейфова смуга (f_transit):  " << res.f_transit_hz * 1e-6 << " МГц\n";
    std::cout << "Результуюча смуга f_3dB:     " << res.f_cutoff_3db_hz * 1e-6 << " МГц\n";
    std::cout << std::scientific << std::setprecision(2);
    std::cout << "Шумова густина струму:       " << res.noise_current_density_a_rthz << " А/sqrt(Гц)\n";
    std::cout << "Поріг чутливості NEP:        " << res.nep_w_rthz << " Вт/sqrt(Гц)\n";

    return 0;
}
