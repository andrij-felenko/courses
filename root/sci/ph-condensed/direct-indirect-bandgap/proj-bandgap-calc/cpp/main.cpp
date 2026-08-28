// cpp
#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <iomanip>
#include <numbers>

struct Semiconductor {
    std::string name;
    double bandgap_ev;            // E_g в еВ
    bool is_direct;               // true - прямий, false - непрямий
    double coeff;                 // Коефіцієнт поглинання
    double phonon_ev = 0.0;       // Енергія фонона для непрямих переходів
    double direct_sec_ev = 0.0;   // Енергія прямого переходу для непрямого
};

class AbsorptionCalculator {
public:
    static constexpr double k_b_ev = 8.61733324e-5;

    explicit AbsorptionCalculator(double temperature_k = 300.0)
        : temp_k_(temperature_k) {}

    [[nodiscard]] double calculate_alpha(const Semiconductor& semi, double photon_ev) const {
        if (photon_ev < semi.bandgap_ev && semi.is_direct) {
            return 0.0;
        }

        if (semi.is_direct) {
            const double delta_e = photon_ev - semi.bandgap_ev;
            return semi.coeff * std::sqrt(delta_e);
        }

        // Перемикання на прямий перехід при високих енергіях
        if (semi.direct_sec_ev > 0.0 && photon_ev >= semi.direct_sec_ev) {
            const double delta_dir = photon_ev - semi.direct_sec_ev;
            return 25000.0 + 60000.0 * std::sqrt(delta_dir);
        }

        double alpha = 0.0;
        const double h_omega = semi.phonon_ev;
        const double kt = k_b_ev * temp_k_;

        // Гілка поглинання фонона
        if (photon_ev >= (semi.bandgap_ev - h_omega)) {
            const double delta_abs = photon_ev - semi.bandgap_ev + h_omega;
            const double arg = h_omega / kt;
            const double n_q = (arg < 80.0) ? (1.0 / (std::exp(arg) - 1.0)) : 0.0;
            alpha += semi.coeff * delta_abs * delta_abs * n_q;
        }

        // Гілка випромінювання фонона
        if (photon_ev >= (semi.bandgap_ev + h_omega)) {
            const double delta_em = photon_ev - semi.bandgap_ev - h_omega;
            const double arg = -h_omega / kt;
            const double n_q_plus_1 = (arg > -80.0) ? (1.0 / (1.0 - std::exp(arg))) : 1.0;
            alpha += semi.coeff * delta_em * delta_em * n_q_plus_1;
        }

        return alpha;
    }

    [[nodiscard]] static double calculate_required_depth_um(double alpha_cm1, double target_absorption = 0.95) {
        if (alpha_cm1 <= 1e-6) {
            return 1e9;
        }
        const double d_cm = -std::log(1.0 - target_absorption) / alpha_cm1;
        return d_cm * 1e4; // см -> мкм
    }

private:
    double temp_k_;
};

int main() {
    const std::vector<Semiconductor> materials{
        {"Арсенід галію (GaAs)", 1.42, true,  45000.0, 0.0,   0.0},
        {"Нітрид галію (GaN)",   3.40, true, 120000.0, 0.0,   0.0},
        {"Кремній (Si)",         1.12, false,  3200.0, 0.051, 3.40},
        {"Германій (Ge)",        0.66, false,  2800.0, 0.028, 0.80}
    };

    const AbsorptionCalculator calc(300.0);
    const std::vector<double> energies{1.2, 1.4, 1.5, 1.8, 2.0, 2.5, 3.5};

    std::cout << std::left << std::setw(22) << "Матеріал" 
              << " | " << std::setw(8)  << "h*nu (еВ)" 
              << " | " << std::setw(12) << "alpha (см^-1)" 
              << " | " << std::setw(14) << "d_95% (мкм)\n";
    std::cout << std::string(65, '-') << "\n";

    for (const double e_photon : energies) {
        for (const auto& semi : materials) {
            const double alpha = calc.calculate_alpha(semi, e_photon);
            const double depth_um = AbsorptionCalculator::calculate_required_depth_um(alpha, 0.95);

            std::cout << std::left << std::setw(22) << semi.name
                      << " | " << std::right << std::setw(8) << std::fixed << std::setprecision(2) << e_photon;

            if (alpha > 0.0) {
                std::cout << " | " << std::setw(12) << std::setprecision(1) << alpha
                          << " | " << std::setw(14) << std::setprecision(2) << depth_um << "\n";
            } else {
                std::cout << " | " << std::setw(12) << "0.0 (прозорий)"
                          << " | " << std::setw(14) << "N/A" << "\n";
            }
        }
        std::cout << std::string(65, '-') << "\n";
    }

    return 0;
}
