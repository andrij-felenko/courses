#include <cmath>
#include <numbers>

namespace quantum::duality {

constexpr double C_LIGHT = 299792458.0;
constexpr double H_PLANCK = 6.62607015e-34;
constexpr double E_CHARGE = 1.602176634e-19;
constexpr double M_ELECTRON = 9.1093837015e-31;
constexpr double M_NEUTRON = 1.67492749804e-27;
constexpr double M_PROTON = 1.67262192369e-27;

[[nodiscard]] std::expected<CalculationOutput, CalculationError> 
compute_debroglie_parameters(const CalculationInput& input) noexcept {
    CalculationOutput out{};
    
    // Визначення маси частинки
    switch (input.particle) {
        case ParticleType::Electron:      out.mass_kg = M_ELECTRON; break;
        case ParticleType::Neutron:       out.mass_kg = M_NEUTRON; break;
        case ParticleType::Proton:        out.mass_kg = M_PROTON; break;
        case ParticleType::AlphaParticle: out.mass_kg = 6.644657230e-27; break;
        case ParticleType::Custom:
            if (input.custom_mass_kg <= 0.0) {
                return std::unexpected(CalculationError::InvalidMass);
            }
            out.mass_kg = input.custom_mass_kg;
            break;
    }
    
    // Визначення кінетичної енергії E_k (у джоулях)
    double E_k = 0.0;
    if (input.accelerating_voltage_v > 0.0 && input.particle == ParticleType::Electron) {
        E_k = input.accelerating_voltage_v * E_CHARGE;
    } else if (input.kinetic_energy_ev > 0.0) {
        E_k = input.kinetic_energy_ev * E_CHARGE;
    } else {
        return std::unexpected(CalculationError::InvalidKineticEnergy);
    }
    
    double E_rest = out.mass_kg * C_LIGHT * C_LIGHT;
    out.is_relativistic = (E_k > 0.05 * E_rest);
    
    if (out.is_relativistic) {
        // Повний релятивістський розрахунок
        out.momentum_kg_m_s = (1.0 / C_LIGHT) * std::sqrt(E_k * (E_k + 2.0 * E_rest));
        out.debroglie_wavelength_m = H_PLANCK / out.momentum_kg_m_s;
        out.velocity_m_s = C_LIGHT * std::sqrt(1.0 - (E_rest * E_rest) / ((E_k + E_rest) * (E_k + E_rest)));
        out.group_velocity_m_s = out.velocity_m_s;
        out.phase_velocity_m_s = (C_LIGHT * C_LIGHT) / out.velocity_m_s;
    } else {
        // Класичний нерелятивістський розрахунок
        out.momentum_kg_m_s = std::sqrt(2.0 * out.mass_kg * E_k);
        out.debroglie_wavelength_m = H_PLANCK / out.momentum_kg_m_s;
        out.velocity_m_s = out.momentum_kg_m_s / out.mass_kg;
        out.group_velocity_m_s = out.velocity_m_s;
        out.phase_velocity_m_s = out.velocity_m_s / 2.0;
    }
    
    // Перевірка кристалографічних обмежень Бреґґа
    if (input.crystal_spacing_m <= 0.0) {
        return std::unexpected(CalculationError::InvalidCrystalSpacing);
    }
    
    double sin_bragg = out.debroglie_wavelength_m / (2.0 * input.crystal_spacing_m);
    if (sin_bragg <= 1.0) {
        out.bragg_angle_rad = std::asin(sin_bragg);
    } else {
        out.bragg_angle_rad = std::numeric_limits<double>::quiet_NaN();
    }
    
    // Перевірка апертури мікроскопа
    if (input.numerical_aperture <= 0.0 || input.numerical_aperture > 1.4) {
        return std::unexpected(CalculationError::NumericalApertureOutOfRange);
    }
    out.microscope_resolution_m = out.debroglie_wavelength_m / (2.0 * input.numerical_aperture);
    
    return out;
}

} // namespace quantum::duality
