#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <numbers>
#include <string>

namespace fermi_physics {

constexpr double HBAR = 1.054571817e-34;
constexpr double M_E  = 9.1093837015e-31;
constexpr double KB   = 1.380649e-23;
constexpr double EV   = 1.602176634e-19;

class QuantumFermiGas {
public:
    explicit QuantumFermiGas(double electron_density)
        : n_(electron_density),
          E_F_((HBAR * HBAR / (2.0 * M_E)) * std::pow(3.0 * std::numbers::pi * std::numbers::pi * electron_density, 2.0 / 3.0)),
          T_F_(E_F_ / KB) {}

    [[nodiscard]] double fermi_energy() const noexcept { return E_F_; }
    [[nodiscard]] double fermi_temperature() const noexcept { return T_F_; }

    [[nodiscard]] static double density_of_states(double E) noexcept {
        if (E <= 0.0) return 0.0;
        const double coeff = (1.0 / (2.0 * std::numbers::pi * std::numbers::pi)) * 
                             std::pow((2.0 * M_E) / (HBAR * HBAR), 1.5);
        return coeff * std::sqrt(E);
    }

    [[nodiscard]] static double fermi_dirac(double E, double mu, double T) noexcept {
        if (T <= 0.0) return (E <= mu) ? 1.0 : 0.0;
        const double x = (E - mu) / (KB * T);
        if (x > 100.0) return 0.0;
        if (x < -100.0) return 1.0;
        return 1.0 / (std::exp(x) + 1.0);
    }

    [[nodiscard]] double compute_chemical_potential(double T, std::size_t steps = 3000) const {
        if (T <= 0.0) return E_F_;

        double low = 0.0;
        double high = 2.0 * E_F_;
        const double E_max = E_F_ + 10.0 * KB * T;
        double mu = E_F_;

        auto integrate_n = [&](double test_mu) {
            const double dE = E_max / static_cast<double>(steps);
            double sum = 0.5 * (density_of_states(0.0) * fermi_dirac(0.0, test_mu, T) +
                               density_of_states(E_max) * fermi_dirac(E_max, test_mu, T));
            for (std::size_t i = 1; i < steps; ++i) {
                const double E = static_cast<double>(i) * dE;
                sum += density_of_states(E) * fermi_dirac(E, test_mu, T);
            }
            return sum * dE;
        };

        for (int iter = 0; iter < 60; ++iter) {
            mu = 0.5 * (low + high);
            const double n_calc = integrate_n(mu);
            if (std::abs(n_calc - n_) / n_ < 1e-7) break;
            if (n_calc < n_) {
                low = mu;
            } else {
                high = mu;
            }
        }
        return mu;
    }

    [[nodiscard]] double compute_internal_energy_density(double T, double mu, std::size_t steps = 3000) const {
        const double E_max = E_F_ + 10.0 * KB * T;
        const double dE = E_max / static_cast<double>(steps);
        double sum = 0.5 * (0.0 + E_max * density_of_states(E_max) * fermi_dirac(E_max, mu, T));
        for (std::size_t i = 1; i < steps; ++i) {
            const double E = static_cast<double>(i) * dE;
            sum += E * density_of_states(E) * fermi_dirac(E, mu, T);
        }
        return sum * dE;
    }

    [[nodiscard]] double heat_capacity_numerical(double T, double dT = 2.0) const {
        const double mu_plus = compute_chemical_potential(T + dT);
        const double mu_minus = compute_chemical_potential(T - dT);
        
        const double u_plus = compute_internal_energy_density(T + dT, mu_plus);
        const double u_minus = compute_internal_energy_density(T - dT, mu_minus);
        
        return (u_plus - u_minus) / (2.0 * dT);
    }

    [[nodiscard]] double heat_capacity_sommerfeld(double T) const noexcept {
        return (std::numbers::pi * std::numbers::pi / 2.0) * n_ * KB * (T / T_F_);
    }

private:
    double n_;
    double E_F_;
    double T_F_;
};

} // namespace fermi_physics

int main() {
    using namespace fermi_physics;

    // Концентрація вільних електронів міді (Cu)
    constexpr double n_copper = 8.47e28;
    const QuantumFermiGas gas(n_copper);

    std::cout << "=== МОДЕЛЮВАННЯ ВИРОДЖЕНОГО ЕЛЕКТРОННОГО ГАЗУ (C++) ===\n";
    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Енергія Фермі E_F     = " << gas.fermi_energy() / EV << " eV\n";
    std::cout << "Температура Фермі T_F = " << gas.fermi_temperature() << " K\n\n";

    std::cout << std::setw(8)  << "T (K)" 
              << std::setw(14) << "mu (eV)" 
              << std::setw(14) << "mu / E_F" 
              << std::setw(18) << "C_v чисельна" 
              << std::setw(18) << "C_v Зоммерфельд\n";
    std::cout << std::string(72, '-') << "\n";

    for (double T = 100.0; T <= 2000.0; T += 300.0) {
        const double mu = gas.compute_chemical_potential(T);
        const double cv_num = gas.heat_capacity_numerical(T);
        const double cv_theory = gas.heat_capacity_sommerfeld(T);

        std::cout << std::setw(8)  << std::setprecision(1) << T 
                  << std::setw(14) << std::setprecision(5) << mu / EV
                  << std::setw(14) << std::setprecision(5) << mu / gas.fermi_energy()
                  << std::setw(18) << std::setprecision(2) << cv_num
                  << std::setw(18) << std::setprecision(2) << cv_theory << "\n";
    }

    return 0;
}
