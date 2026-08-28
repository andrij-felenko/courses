#pragma once

#include <string>
#include <optional>
#include <stdexcept>
#include <span>

namespace physics::thermodynamics {

constexpr double R_GAS_CONST = 8.314462618;
constexpr double KB_BOLTZMANN = 1.380649e-23;
constexpr double NA_AVOGADRO = 6.02214076e23;

enum class GasType {
    Ideal,
    Helium,
    Hydrogen,
    Nitrogen,
    Oxygen,
    Air,
    CO2,
    Methane,
    WaterVapor
};

struct VanDerWaalsParams {
    double a_pa_m6_mol2; // Па·м⁶/моль²
    double b_m3_mol;     // м³/моль
    double molar_mass;   // кг/моль
};

class GasState {
public:
    GasState(double mass_kg, double molar_mass_kg_mol, GasType type = GasType::Ideal)
        : mass_kg_(mass_kg), molar_mass_(molar_mass_kg_mol), type_(type) {
        if (mass_kg <= 0.0 || molar_mass_kg_mol <= 0.0) {
            throw std::invalid_argument("Маса та молярна маса повинні бути додатними!");
        }
    }

    double moles() const noexcept { return mass_kg_ / molar_mass_; }
    double mass() const noexcept { return mass_kg_; }
    double molar_mass() const noexcept { return molar_mass_; }
    GasType type() const noexcept { return type_; }

    // Обчислення тиску за рівнянням ідеального газу
    double solve_pressure(double volume_m3, double temp_k) const {
        check_positive(volume_m3, temp_k);
        return (moles() * R_GAS_CONST * temp_k) / volume_m3;
    }

    // Обчислення об'єму за рівнянням ідеального газу
    double solve_volume(double pressure_pa, double temp_k) const {
        check_positive(pressure_pa, temp_k);
        return (moles() * R_GAS_CONST * temp_k) / pressure_pa;
    }

    // Обчислення температури за рівнянням ідеального газу
    double solve_temperature(double pressure_pa, double volume_m3) const {
        check_positive(pressure_pa, volume_m3);
        return (pressure_pa * volume_m3) / (moles() * R_GAS_CONST);
    }

    // Обчислення тиску за рівнянням Ван-дер-Ваальса
    double solve_vdw_pressure(double volume_m3, double temp_k, const VanDerWaalsParams& params) const {
        check_positive(volume_m3, temp_k);
        double n = moles();
        double v_m = volume_m3 / n; // Молярний об'єм
        if (v_m <= params.b_m3_mol) {
            throw std::domain_error("Молярний об'єм менший за власний об'єм молекул b!");
        }
        double term1 = (R_GAS_CONST * temp_k) / (v_m - params.b_m3_mol);
        double term2 = params.a_pa_m6_mol2 / (v_m * v_m);
        return term1 - term2;
    }

    // Коефіцієнт стискуваності Z = P * V / (n * R * T)
    static double compressibility_factor(double pressure_pa, double volume_m3, double moles, double temp_k) {
        return (pressure_pa * volume_m3) / (moles * R_GAS_CONST * temp_k);
    }

private:
    static void check_positive(double a, double b) {
        if (a <= 0.0 || b <= 0.0) {
            throw std::invalid_argument("Термодинамічні параметри повинні бути строго додатними!");
        }
    }

    double mass_kg_;
    double molar_mass_;
    GasType type_;
};

} // namespace physics::thermodynamics
