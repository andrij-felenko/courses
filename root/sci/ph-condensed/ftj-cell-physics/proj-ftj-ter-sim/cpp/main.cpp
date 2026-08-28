#include <iostream>
#include <cmath>
#include <vector>
#include <iomanip>
#include <span>

namespace ftj {

// Елементарні фундаментальні константи
constexpr double e0    = 1.602176634e-19;  // Кл
constexpr double m_e   = 9.1093837015e-31; // кг
constexpr double hbar  = 1.054571817e-34;  // Дж·с
constexpr double eps0  = 8.8541878128e-12; // Ф/м

// Параметри структури FTJ
struct CellParameters {
    double barrier_thickness_nm{2.0};
    double effective_mass_ratio{0.5};
    double phi0_ev{1.2};
    double polarization_uc_cm2{20.0};
    double lambda1_angstrom{0.8};
    double lambda2_angstrom{0.2};
    double eps_r{25.0};
};

// Результат точкового розрахунку ВАХ
struct SimulationResult {
    double v_read_volts;
    double j_on_a_cm2;
    double j_off_a_cm2;
    double r_on_ohm_cm2;
    double r_off_ohm_cm2;
    double ter_percent;
};

class Simulator {
public:
    explicit Simulator(CellParameters params) : p_(params) {}

    [[nodiscard]] double calculate_barrier_shift() const noexcept {
        const double d_m = p_.barrier_thickness_nm * 1.0e-9;
        const double p_c_m2 = p_.polarization_uc_cm2 * 1.0e-2;
        const double l1_m = p_.lambda1_angstrom * 1.0e-10;
        const double l2_m = p_.lambda2_angstrom * 1.0e-10;

        const double k_scr = (e0 / (eps0 * p_.eps_r)) * 
                             ((l1_m - l2_m) / (d_m + l1_m + l2_m));
        
        return (k_scr * p_c_m2) / e0; // еВ
    }

    [[nodiscard]] double tunnel_current_density(double v_volts, double phi_ev) const noexcept {
        phi_ev = std::max(phi_ev, 0.01);
        const double d_m = p_.barrier_thickness_nm * 1.0e-9;
        const double m_eff = p_.effective_mass_ratio * m_e;
        const double phi_j = phi_ev * e0;
        const double v_j = std::abs(v_volts) * e0;

        const double a_const = (2.0 * std::sqrt(2.0 * m_eff)) / hbar;
        double phi_eff = std::max(phi_j - v_j / 2.0, 0.001 * e0);

        const double d_factor = std::exp(-a_const * d_m * std::sqrt(phi_eff));
        const double c0 = (e0 * e0 * std::sqrt(2.0 * m_eff)) / 
                          (4.0 * M_PI * M_PI * hbar * hbar * d_m);

        const double j_a_m2 = c0 * v_volts * std::sqrt(phi_eff / e0) * d_factor;
        return j_a_m2 * 1.0e-4; // А/см²
    }

    [[nodiscard]] SimulationResult run_point(double v_read) const noexcept {
        const double delta_phi = calculate_barrier_shift();
        const double phi_on = p_.phi0_ev - delta_phi;
        const double phi_off = p_.phi0_ev + delta_phi;

        const double j_on = tunnel_current_density(v_read, phi_on);
        const double j_off = tunnel_current_density(v_read, phi_off);

        const double r_on = (j_on > 0.0) ? (v_read / j_on) : 1.0e12;
        const double r_off = (j_off > 0.0) ? (v_read / j_off) : 1.0e12;

        const double ter_ratio = (j_off > 0.0) ? (j_on / j_off) : 1.0;
        const double ter_pct = (ter_ratio - 1.0) * 100.0;

        return {v_read, j_on, j_off, r_on, r_off, ter_pct};
    }

    [[nodiscard]] std::vector<SimulationResult> sweep_voltage(std::span<const double> voltages) const {
        std::vector<SimulationResult> results;
        results.reserve(voltages.size());
        for (double v : voltages) {
            results.push_back(run_point(v));
        }
        return results;
    }

private:
    CellParameters p_;
};

} // namespace ftj

int main() {
    using namespace ftj;

    const CellParameters cell{
        .barrier_thickness_nm = 2.0,
        .effective_mass_ratio = 0.5,
        .phi0_ev = 1.2,
        .polarization_uc_cm2 = 20.0,
        .lambda1_angstrom = 0.8,
        .lambda2_angstrom = 0.2,
        .eps_r = 25.0
    };

    const Simulator sim(cell);
    const std::vector<double> v_steps = {0.01, 0.03, 0.05, 0.07, 0.09};

    std::cout << "=== Симуляція FTJ (C++20 реалізація) ===\n";
    std::cout << "Товщина d = " << cell.barrier_thickness_nm << " нм, P = " 
              << cell.polarization_uc_cm2 << " мкКл/см²\n\n";

    std::cout << std::setw(10) << "V_read (В)" << " | "
              << std::setw(13) << "J_ON (А/см²)" << " | "
              << std::setw(13) << "J_OFF (А/см²)" << " | "
              << std::setw(13) << "R_ON (Ом·см²)" << " | "
              << std::setw(13) << "R_OFF (Ом·см²)" << " | "
              << std::setw(10) << "TER (%)" << "\n";
    std::cout << std::string(87, '-') << "\n";

    const auto results = sim.sweep_voltage(v_steps);
    for (const auto& r : results) {
        std::cout << std::setw(10) << std::fixed << std::setprecision(2) << r.v_read_volts << " | "
                  << std::setw(13) << std::scientific << std::setprecision(3) << r.j_on_a_cm2 << " | "
                  << std::setw(13) << std::scientific << std::setprecision(3) << r.j_off_a_cm2 << " | "
                  << std::setw(13) << std::scientific << std::setprecision(3) << r.r_on_ohm_cm2 << " | "
                  << std::setw(13) << std::scientific << std::setprecision(3) << r.r_off_ohm_cm2 << " | "
                  << std::setw(10) << std::fixed << std::setprecision(1) << r.ter_percent << "%\n";
    }

    return 0;
}
