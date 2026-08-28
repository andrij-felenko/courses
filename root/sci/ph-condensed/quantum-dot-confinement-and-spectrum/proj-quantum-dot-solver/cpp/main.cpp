#include <iostream>
#include <vector>
#include <cmath>
#include <string>
#include <iomanip>
#include <stdexcept>
#include <algorithm>
#include <numeric>

// Фізичні константи (СІ)
constexpr double HBAR = 1.054571817e-34;           // Дж·с
constexpr double EV_TO_JOULE = 1.602176634e-19;     // 1 еВ у Джоулях
constexpr double ELECTRON_MASS = 9.1093837015e-31;  // кг
constexpr double E_CHARGE = 1.602176634e-19;        // Кл
constexpr double EPSILON_0 = 8.8541878128e-12;      // Ф/м
constexpr double PI = 3.14159265358979323846;

struct QuantumDotMaterial {
    std::string name;
    double eg_bulk_ev;
    double me_eff;  // у масах вільного електрона
    double mh_eff;  // у масах вільного електрона
    double eps_r;

    [[nodiscard]] double reduced_mass_kg() const noexcept {
        double me_kg = me_eff * ELECTRON_MASS;
        double mh_kg = mh_eff * ELECTRON_MASS;
        return (me_kg * mh_kg) / (me_kg + mh_kg);
    }

    [[nodiscard]] double rydberg_energy_ev() const noexcept {
        double mu = reduced_mass_kg();
        double ryd_j = (mu * std::pow(E_CHARGE, 4.0)) / 
                       (2.0 * std::pow(4.0 * PI * EPSILON_0 * eps_r, 2.0) * HBAR * HBAR);
        return ryd_j / EV_TO_JOULE;
    }
};

struct SpectrumResult {
    std::vector<double> normalized_absorption;
    double peak_energy_ev;
    double peak_wavelength_nm;
};

class BrusSolver {
public:
    static double calculate_bandgap_ev(const QuantumDotMaterial& mat, double radius_nm) {
        if (radius_nm <= 0.5) {
            throw std::invalid_argument("Радіус квантової точки має бути більшим за 0.5 нм");
        }

        double r_m = radius_nm * 1e-9;
        double mu_kg = mat.reduced_mass_kg();

        // 1. Кінетичний доданок конфайнменту (1/R²)
        double e_conf_joules = (HBAR * HBAR * PI * PI) / (2.0 * mu_kg * r_m * r_m);
        double e_conf_ev = e_conf_joules / EV_TO_JOULE;

        // 2. Кулонівський доданок притягання (1/R)
        double e_coulomb_joules = (1.786 * E_CHARGE * E_CHARGE) / (4.0 * PI * EPSILON_0 * mat.eps_r * r_m);
        double e_coulomb_ev = e_coulomb_joules / EV_TO_JOULE;

        // 3. Поляризаційна поправка
        double e_pol_ev = 0.248 * mat.rydberg_energy_ev();

        return mat.eg_bulk_ev + e_conf_ev - e_coulomb_ev - e_pol_ev;
    }

    static double energy_to_wavelength_nm(double energy_ev) noexcept {
        return 1239.84193 / energy_ev;
    }

    static SpectrumResult compute_ensemble_spectrum(
        const QuantumDotMaterial& mat,
        double r_mean_nm,
        double r_std_nm,
        const std::vector<double>& energy_grid_ev,
        double homogeneous_gamma_ev = 0.03
    ) {
        constexpr int num_samples = 300;
        double r_min = std::max(0.6, r_mean_nm - 3.5 * r_std_nm);
        double r_max = r_mean_nm + 3.5 * r_std_nm;
        double dr = (r_max - r_min) / num_samples;

        std::vector<double> absorption(energy_grid_ev.size(), 0.0);

        for (int i = 0; i < num_samples; ++i) {
            double r = r_min + (i + 0.5) * dr;
            double p_r = (1.0 / (r_std_nm * std::sqrt(2.0 * PI))) * 
                         std::exp(-0.5 * std::pow((r - r_mean_nm) / r_std_nm, 2.0));
            double eg_r = calculate_bandgap_ev(mat, r);

            for (size_t j = 0; j < energy_grid_ev.size(); ++j) {
                double diff = (energy_grid_ev[j] - eg_r) / homogeneous_gamma_ev;
                double line_shape = std::exp(-0.5 * diff * diff);
                absorption[j] += p_r * line_shape * dr;
            }
        }

        auto max_it = std::max_element(absorption.begin(), absorption.end());
        double max_val = *max_it;
        size_t peak_idx = std::distance(absorption.begin(), max_it);

        if (max_val > 0.0) {
            for (auto& val : absorption) {
                val /= max_val;
            }
        }

        double peak_energy = energy_grid_ev[peak_idx];
        double peak_wl = energy_to_wavelength_nm(peak_energy);

        return {std::move(absorption), peak_energy, peak_wl};
    }
};

int main() {
    std::vector<QuantumDotMaterial> materials = {
        {"CdSe", 1.74, 0.13, 0.45, 9.3},
        {"InP",  1.35, 0.07, 0.60, 12.5},
        {"PbS",  0.41, 0.09, 0.09, 17.2}
    };

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "=== ОБЧИСЛЕННЯ СПЕКТРАЛЬНИХ ХАРАКТЕРИСТИК КВАНТОВИХ ТОЧОК (C++20) ===\n";

    for (const auto& mat : materials) {
        std::cout << "\n--- Матеріал: " << mat.name << " (E_g bulk = " << mat.eg_bulk_ev << " еВ) ---\n";
        for (double r_nm : {2.0, 3.5, 5.0}) {
            double eg_ev = BrusSolver::calculate_bandgap_ev(mat, r_nm);
            double wl_nm = BrusSolver::energy_to_wavelength_nm(eg_ev);
            std::cout << "Радіус R = " << r_nm << " нм | E_g(R) = " << eg_ev 
                      << " еВ | Довжина хвилі λ = " << wl_nm << " нм\n";
        }

        std::vector<double> energy_grid;
        for (int i = 0; i < 300; ++i) {
            energy_grid.push_back(1.0 + i * 0.01);
        }

        auto res = BrusSolver::compute_ensemble_spectrum(mat, 3.0, 0.2, energy_grid);
        std::cout << "Ансамбль R_0 = 3.0±0.2 нм -> Пік поглинання: " 
                  << res.peak_energy_ev << " еВ (" << res.peak_wavelength_nm << " нм)\n";
    }

    return 0;
}
