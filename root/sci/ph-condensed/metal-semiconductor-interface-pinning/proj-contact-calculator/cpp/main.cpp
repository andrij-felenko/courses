#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <numbers>

namespace physics {
    constexpr double q_elem   = 1.602176634e-19; /* Кл */
    constexpr double k_boltz  = 1.380649e-23;    /* Дж/К */
    constexpr double eps_0    = 8.854187817e-12; /* Ф/м */
    constexpr double h_planck = 6.62607015e-34;  /* Дж·с */
    constexpr double hbar     = 1.054571817e-34;  /* Дж·с */
    constexpr double m0       = 9.1093837015e-31; /* кг */

    struct SchottkyParameters {
        double barrier_height_ev{0.75}; /* еВ */
        double doping_m3{1.0e22};        /* м⁻³ */
        double rel_permittivity{11.7};  /* Si */
        double rel_effective_mass{0.26};
        double temperature_k{300.0};    /* К */
        double area_m2{1.0e-8};         /* м² */
        double series_resistance{15.0}; /* Ом */
    };

    class SchottkyDiodeSimulator {
    public:
        explicit SchottkyDiodeSimulator(SchottkyParameters params)
            : p_(params) {}

        [[nodiscard]] double richardson_constant() const noexcept {
            const double m_eff = p_.rel_effective_mass * m0;
            return (4.0 * std::numbers::pi * q_elem * m_eff * k_boltz * k_boltz) / 
                   (h_planck * h_planck * h_planck);
        }

        [[nodiscard]] double compute_current(double external_voltage) const {
            const double vt = (k_boltz * p_.temperature_k) / q_elem;
            const double a_star = richardson_constant();
            const double saturation_current_density = a_star * p_.temperature_k * p_.temperature_k * 
                                                     std::exp(-p_.barrier_height_ev / vt);
            const double i_sat = saturation_current_density * p_.area_m2;

            double v_barrier = external_voltage;
            constexpr int max_iterations = 100;
            constexpr double tolerance = 1e-12;

            for (int i = 0; i < max_iterations; ++i) {
                const double current = i_sat * (std::exp(v_barrier / (1.02 * vt)) - 1.0);
                const double f_val = v_barrier + current * p_.series_resistance - external_voltage;
                const double df_val = 1.0 + (current + i_sat) * (p_.series_resistance / (1.02 * vt));

                const double next_v = v_barrier - f_val / df_val;
                if (std::abs(next_v - v_barrier) < tolerance) {
                    v_barrier = next_v;
                    break;
                }
                v_barrier = next_v;
            }

            return i_sat * (std::exp(v_barrier / (1.02 * vt)) - 1.0);
        }

        [[nodiscard]] static double compute_specific_contact_resistance(
            double barrier_ev, double doping_cm3, double m_eff_rel, double eps_r) noexcept {
            
            const double n_d_m3 = doping_cm3 * 1.0e6;
            const double m_eff = m_eff_rel * m0;
            const double eps_s = eps_r * eps_0;

            /* Характеристична енергія E_00 Падовані-Стратона */
            const double e_00 = (q_elem * hbar / 2.0) * std::sqrt(n_d_m3 / (m_eff * eps_s));
            const double e_00_ev = e_00 / q_elem;

            const double rho_c_m2 = std::exp(barrier_ev / e_00_ev);
            return rho_c_m2 * 1.0e4 * 1.0e-11;
        }

    private:
        SchottkyParameters p_;
    };
}

int main() {
    using namespace physics;

    SchottkyParameters params{
        .barrier_height_ev = 0.75,
        .doping_m3 = 1.0e22,
        .rel_permittivity = 11.7,
        .rel_effective_mass = 0.26,
        .temperature_k = 300.0,
        .area_m2 = 1.0e-8,
        .series_resistance = 15.0
    };

    SchottkyDiodeSimulator simulator(params);

    std::cout << "=== МОДЕЛЮВАННЯ ВАХ КОНТАКТУ МЕТАЛ-НАПІВПРОВІДНИК (C++) ===\n";
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Напруга V (В) | Струм I (мА)\n";
    std::cout << "-------------------------------\n";

    for (double v = -0.5; v <= 0.61; v += 0.1) {
        double current_ma = simulator.compute_current(v) * 1000.0;
        std::cout << "    " << std::setw(5) << v << "     |   " 
                  << std::scientific << std::setprecision(4) << current_ma << "\n"
                  << std::fixed << std::setprecision(2);
    }

    std::cout << "\n=== РОЗРАХУНОК ПИТОМОГО ОПОРУ ТУНЕЛЬНОГО КОНТАКТУ ===\n";
    std::cout << "Легування N_d (см⁻³) | Питомий опір rho_c (Ом·см²)\n";
    std::cout << "-------------------------------------------------\n";

    const std::vector<double> doping_levels{1.0e17, 1.0e18, 1.0e19, 1.0e20};
    for (double nd : doping_levels) {
        double rho_c = SchottkyDiodeSimulator::compute_specific_contact_resistance(0.65, nd, 0.26, 11.7);
        std::cout << "      " << std::scientific << std::setprecision(1) << nd 
                  << "        |        " << std::setprecision(3) << rho_c << "\n";
    }

    return 0;
}
