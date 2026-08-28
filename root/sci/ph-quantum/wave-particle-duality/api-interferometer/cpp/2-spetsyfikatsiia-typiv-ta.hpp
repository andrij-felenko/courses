#pragma once

#include <cstdint>
#include <string_view>
#include <expected>
#include <numbers>

namespace quantum::duality {

// Типи фундаментальних та складених частинок
enum class ParticleType : uint8_t {
    Electron,       // Електрон (m_e = 9.109383e-31 кг)
    Neutron,        // Нейтрон (m_n = 1.674927e-27 кг)
    Proton,         // Протон (m_p = 1.672621e-27 кг)
    AlphaParticle,  // Альфа-частинка (ядро Гелію-4)
    Custom          // Користувацька частинка (маса передається у custom_mass_kg)
};

// Вхідні параметри квантового розрахунку
struct CalculationInput {
    ParticleType particle = ParticleType::Electron;
    double custom_mass_kg = 0.0;          // Використовується при ParticleType::Custom (кг)
    double kinetic_energy_ev = 0.0;       // Кінетична енергія E_k в електрон-вольтах (eV)
    double accelerating_voltage_v = 0.0;  // Прискорювальна напруга V (В); якщо > 0, перераховує E_k
    double crystal_spacing_m = 0.091e-9;  // Міжатомна відстань кристала d (м)
    double numerical_aperture = 0.01;        // Чисельна апертура об'єктива мікроскопа (NA)
};

// Результат розрахунку параметрів де Бройля
struct CalculationOutput {
    double mass_kg = 0.0;                 // Маса спокою частинки (кг)
    double momentum_kg_m_s = 0.0;         // Релятивістський імпульс (кг·м/с)
    double velocity_m_s = 0.0;            // Швидкість частинки v (м/с)
    double debroglie_wavelength_m = 0.0;     // Довжина хвилі де Бройля λ (м)
    double phase_velocity_m_s = 0.0;      // Фазова швидкість v_p (м/с)
    double group_velocity_m_s = 0.0;      // Групова швидкість v_g (м/с)
    double bragg_angle_rad = 0.0;         // Кут дифракції Бреґґа θ (радіани)
    double microscope_resolution_m = 0.0; // Межа роздільності мікроскопа (м)
    bool is_relativistic = false;         // Прапорець релятивістського режиму (v > 0.1 c)
};

// Коди помилок розрахунку
enum class CalculationError : uint8_t {
    InvalidKineticEnergy,
    InvalidMass,
    InvalidCrystalSpacing,
    NumericalApertureOutOfRange
};

// Публічна функція аналізу параметрів де Бройля
[[nodiscard]] std::expected<CalculationOutput, CalculationError> 
compute_debroglie_parameters(const CalculationInput& input) noexcept;

} // namespace quantum::duality
