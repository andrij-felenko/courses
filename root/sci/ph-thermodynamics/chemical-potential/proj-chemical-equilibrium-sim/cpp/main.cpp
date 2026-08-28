#include <iostream>
#include <cmath>
#include <iomanip>
#include <numbers>
#include <vector>
#include <expected>
#include <string>

namespace Physics {

// Обчислювальний клас для Fermi-газу з RAII та шаблонами типу
class FermiGasSolver {
public:
    static constexpr double KB_EV = 8.617333262e-5; // eV/K

    explicit FermiGasSolver(double fermi_energy_ev)
        : fermi_energy_ev_(fermi_energy_ev) {}

    // Обчислення хімічного потенціалу μ(T) у eV
    [[nodiscard]] double chemical_potential(double temp_k) const noexcept {
        if (temp_k <= 0.0) {
            return fermi_energy_ev_;
        }
        const double kt = KB_EV * temp_k;
        const double ratio = kt / fermi_energy_ev_;
        
        constexpr double pi = std::numbers::pi;
        const double term2 = (pi * pi / 12.0) * (ratio * ratio);
        const double term4 = (pi * pi * pi * pi / 80.0) * std::pow(ratio, 4.0);

        return fermi_energy_ev_ * (1.0 - term2 - term4);
    }

private:
    double fermi_energy_ev_;
};

// Симуляція фазової рівноваги через рівність хімічних потенціалів
class PhaseEquilibriumSolver {
public:
    static constexpr double R_GAS = 8.314462618; // J/(mol·K)

    struct Parameters {
        double heat_vap_j_mol;  // ΔH_vap (J/mol)
        double ref_temp_k;      // T_ref (K)
        double ref_press_pa;    // P_ref (Pa)
    };

    explicit PhaseEquilibriumSolver(Parameters params)
        : params_(params) {}

    // Знаходження тиску насичення P_sat(T)
    [[nodiscard]] std::expected<double, std::string> saturation_pressure(double temp_k) const {
        if (temp_k <= 0.0) {
            return std::unexpected("Температура повинна бути більшою за абсолютний нуль.");
        }
        const double exponent = (params_.heat_vap_j_mol / R_GAS) * 
                                (1.0 / params_.ref_temp_k - 1.0 / temp_k);
        return params_.ref_press_pa * std::exp(exponent);
    }

private:
    Parameters params_;
};

} // namespace Physics

int main() {
    std::cout << "=== Обчислення хімічного потенціалу та рівноваги (C++) ===\n\n";

    // 1. Обчислення хімічного потенціалу електронів у металі
    const Physics::FermiGasSolver copper(7.00); // E_F = 7.0 eV
    const std::vector<double> temperatures = { 4.2, 77.0, 300.0, 1000.0 };

    std::cout << std::fixed << std::setprecision(6);
    std::cout << "Залежність μ(T) для міді (E_F = 7.000000 eV):\n";
    for (double T : temperatures) {
        double mu = copper.chemical_potential(T);
        std::cout << "  T = " << std::setw(6) << T << " K:  μ = " << mu 
                  << " eV  (Δμ = " << (mu - 7.0) << " eV)\n";
    }

    // 2. Фазова рівновага води
    const Physics::PhaseEquilibriumSolver water({
        .heat_vap_j_mol = 40650.0,
        .ref_temp_k = 373.15,
        .ref_press_pa = 101325.0
    });

    std::cout << "\nТиск насиченої пари води при T = 50 °C:\n";
    auto result = water.saturation_pressure(323.15);
    if (result) {
        std::cout << "  P_sat = " << *result << " Pa (" << (*result / 101325.0) << " atm)\n";
    } else {
        std::cerr << "Помилка: " << result.error() << '\n';
    }

    return 0;
}
