#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <algorithm>

// Сучасна C++17 реалізація самоузгодженого Poisson-Schrödinger розв'язувача 2DEG
class PoissonSchroedinger2DEG {
public:
    struct Config {
        std::size_t grid_points = 250;
        double domain_length_nm = 60.0;
        double effective_mass_ratio = 0.067; // GaAs
        double relative_permittivity = 12.9;
        double sheet_density_cm2 = 3.5e11;   // 3.5e11 см^-2
        double mixing_alpha = 0.12;
        std::size_t max_iterations = 600;
        double convergence_tol_eV = 1e-6;
    };

    explicit PoissonSchroedinger2DEG(Config cfg)
        : cfg_(cfg),
          dz_(cfg.domain_length_nm * 1e-9 / (cfg.grid_points - 1)),
          z_grid_(cfg.grid_points),
          potential_eV_(cfg.grid_points),
          psi0_(cfg.grid_points),
          electron_density_(cfg.grid_points) 
    {
        for (std::size_t i = 0; i < cfg_.grid_points; ++i) {
            z_grid_[i] = i * dz_;
            // Початковий трикутний потенціал 2DEG
            potential_eV_[i] = 0.3 * (z_grid_[i] / (cfg_.domain_length_nm * 1e-9));
        }
    }

    struct SimulationResult {
        double ground_state_energy_meV;
        double peak_position_nm;
        std::size_t iterations_completed;
        bool converged;
    };

    SimulationResult run() {
        const double m_eff = cfg_.effective_mass_ratio * m0_;
        const double ns_m2 = cfg_.sheet_density_cm2 * 1e4;
        const double t0 = (hbar_ * hbar_) / (2.0 * m_eff * dz_ * dz_);

        double energy_e0_joules = 0.0;
        bool is_converged = false;
        std::size_t completed_iter = 0;

        for (std::size_t iter = 0; iter < cfg_.max_iterations; ++iter) {
            // 1. Крок Шредінгера: Зворотна ітерація для обчислення E0 та psi0
            energy_e0_joules = solveSchroedingerGroundState(t0, m_eff);

            // 2. Оновлення густості носіїв n(z)
            for (std::size_t i = 0; i < cfg_.grid_points; ++i) {
                electron_density_[i] = ns_m2 * (psi0_[i] * psi0_[i]);
            }

            // 3. Крок Пуассона: Розв'язання d2V/dz2 = (e^2 / eps) * n(z)
            std::vector<double> v_calculated = solvePoissonEquation(ns_m2);

            // 4. Перевірка збіжності та самоузгоджене змішування
            double max_diff_eV = 0.0;
            for (std::size_t i = 0; i < cfg_.grid_points; ++i) {
                double v_mixed = cfg_.mixing_alpha * v_calculated[i] + (1.0 - cfg_.mixing_alpha) * potential_eV_[i];
                double diff = std::abs(v_mixed - potential_eV_[i]);
                if (diff > max_diff_eV) max_diff_eV = diff;
                potential_eV_[i] = v_mixed;
            }

            completed_iter = iter + 1;
            if (max_diff_eV < cfg_.convergence_tol_eV) {
                is_converged = true;
                break;
            }
        }

        // Пошук пика густості хвильової функції 2DEG
        auto max_it = std::max_element(psi0_.begin(), psi0_.end());
        std::size_t max_idx = std::distance(psi0_.begin(), max_it);
        double peak_nm = z_grid_[max_idx] * 1e9;

        return {
            (energy_e0_joules / qe_) * 1000.0,
            peak_nm,
            completed_iter,
            is_converged
        };
    }

private:
    static constexpr double hbar_ = 1.0545718e-34;
    static constexpr double qe_   = 1.60217663e-19;
    static constexpr double m0_   = 9.1093837e-31;
    static constexpr double eps0_ = 8.8541878e-12;

    Config cfg_;
    double dz_;
    std::vector<double> z_grid_;
    std::vector<double> potential_eV_;
    std::vector<double> psi0_;
    std::vector<double> electron_density_;

    double solveSchroedingerGroundState(double t0, double m_eff) {
        std::size_t n_pts = cfg_.grid_points;
        
        // Ініціалізація синусоїдою
        for (std::size_t i = 0; i < n_pts; ++i) {
            psi0_[i] = std::sin(M_PI * i / (n_pts - 1));
        }

        normalizePsi(psi0_);

        std::vector<double> h_psi(n_pts, 0.0);
        for (int step = 0; step < 50; ++step) {
            for (std::size_t i = 1; i < n_pts - 1; ++i) {
                double v_joules = potential_eV_[i] * qe_;
                h_psi[i] = (v_joules + 2.0 * t0) * psi0_[i] - t0 * (psi0_[i - 1] + psi0_[i + 1]);
            }
            for (std::size_t i = 1; i < n_pts - 1; ++i) {
                psi0_[i] = psi0_[i] / (h_psi[i] + 1e-30);
            }
            normalizePsi(psi0_);
        }

        double e0 = 0.0;
        for (std::size_t i = 1; i < n_pts - 1; ++i) {
            double v_joules = potential_eV_[i] * qe_;
            double h_elem = (v_joules + 2.0 * t0) * psi0_[i] - t0 * (psi0_[i - 1] + psi0_[i + 1]);
            e0 += psi0_[i] * h_elem * dz_;
        }
        return e0;
    }

    void normalizePsi(std::vector<double>& psi) {
        double norm = 0.0;
        for (double val : psi) norm += val * val * dz_;
        norm = std::sqrt(norm);
        if (norm > 0.0) {
            for (double& val : psi) val /= norm;
        }
    }

    std::vector<double> solvePoissonEquation(double ns_m2) {
        std::size_t n_pts = cfg_.grid_points;
        std::vector<double> a(n_pts), b(n_pts), c(n_pts), d(n_pts), v_out(n_pts);

        double eps = cfg_.relative_permittivity * eps0_;
        double factor = (qe_ * qe_) / eps;

        for (std::size_t i = 1; i < n_pts - 1; ++i) {
            a[i] = 1.0 / (dz_ * dz_);
            b[i] = -2.0 / (dz_ * dz_);
            c[i] = 1.0 / (dz_ * dz_);
            d[i] = factor * electron_density_[i] / qe_;
        }

        b[0] = 1.0; c[0] = 0.0; d[0] = potential_eV_[0];
        a[n_pts-1] = 0.0; b[n_pts-1] = 1.0; d[n_pts-1] = potential_eV_[n_pts-1];

        std::vector<double> c_star(n_pts), d_star(n_pts);
        c_star[0] = c[0] / b[0];
        d_star[0] = d[0] / b[0];

        for (std::size_t i = 1; i < n_pts; ++i) {
            double m = b[i] - a[i] * c_star[i - 1];
            c_star[i] = c[i] / m;
            d_star[i] = (d[i] - a[i] * d_star[i - 1]) / m;
        }

        v_out[n_pts - 1] = d_star[n_pts - 1];
        for (int i = static_cast<int>(n_pts) - 2; i >= 0; --i) {
            v_out[i] = d_star[i] - c_star[i] * v_out[i + 1];
        }

        return v_out;
    }
};

int main() {
    PoissonSchroedinger2DEG::Config cfg;
    cfg.grid_points = 300;
    cfg.sheet_density_cm2 = 4.0e11;
    cfg.domain_length_nm = 50.0;

    PoissonSchroedinger2DEG solver(cfg);
    auto res = solver.run();

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "========================================================\n";
    std::cout << " C++17 Self-Consistent 2DEG Poisson-Schroedinger Solver \n";
    std::cout << "========================================================\n";
    std::cout << "Статус збіжності:    " << (res.converged ? "УСПІШНО" : "НЕ ЗБІГЛОСЯ") << "\n";
    std::cout << "Кількість ітерацій:  " << res.iterations_completed << "\n";
    std::cout << "Енергія підзони E0:  " << res.ground_state_energy_meV << " меВ\n";
    std::cout << "Пік локалізації 2DEG: " << res.peak_position_nm << " нм від межі\n";

    return 0;
}
