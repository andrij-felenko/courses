#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <iomanip>
#include <numbers>
#include <algorithm>

class CarrierMonteCarlo {
public:
    struct Configuration {
        size_t num_particles{2000};
        size_t num_steps{400};
        double electric_field_x{1e5};  // Напруженість поля, В/м
        double tau_phonon{120e-15};    // Час розсіювання на фононах, с
        double tau_impurity{240e-15};  // Час розсіювання на домішках, с
        double temperature_k{300.0};   // Температура ґратки, К
        double effective_mass_ratio{0.26}; // Відносна ефективна маса Si
    };

    struct SimulationReport {
        size_t total_scatterings;
        size_t phonon_scatterings;
        size_t impurity_scatterings;
        double mean_relaxation_time_s;
        double mean_free_path_nm;
        double drift_velocity_ms;
        double mean_energy_ev;
    };

    explicit CarrierMonteCarlo(Configuration cfg)
        : cfg_(cfg),
          m_eff_(cfg.effective_mass_ratio * mass_e0_),
          rng_(42) {}

    [[nodiscard]] SimulationReport execute() {
        const double inv_tau_ph = 1.0 / cfg_.tau_phonon;
        const double inv_tau_imp = 1.0 / cfg_.tau_impurity;
        const double inv_tau_tot = inv_tau_ph + inv_tau_imp;
        const double tau_total = 1.0 / inv_tau_tot;
        const double prob_phonon = inv_tau_ph / inv_tau_tot;

        const double accel_x = -charge_e_ * cfg_.electric_field_x / m_eff_;

        std::vector<Electron> ensemble(cfg_.num_particles);
        std::uniform_real_distribution<double> dist_u(0.0, 1.0);

        // Ініціалізація початкових швидкостей за Максвеллом — Больцманом
        const double v_th = std::sqrt(3.0 * kb_joule_ * cfg_.temperature_k / m_eff_);
        for (auto& e : ensemble) {
            double cos_th = 1.0 - 2.0 * dist_u(rng_);
            double sin_th = std::sqrt(std::max(0.0, 1.0 - cos_th * cos_th));
            double phi = 2.0 * std::numbers::pi * dist_u(rng_);

            e.vx = v_th * sin_th * std::cos(phi);
            e.vy = v_th * sin_th * std::sin(phi);
            e.vz = v_th * cos_th;
        }

        double grand_total_path = 0.0;
        double grand_total_time = 0.0;
        size_t grand_total_events = 0;
        size_t phonon_events = 0;
        size_t impurity_events = 0;

        for (size_t step = 0; step < cfg_.num_steps; ++step) {
            for (auto& e : ensemble) {
                // 1. Час вільного прольоту
                double u = std::max(1e-12, dist_u(rng_));
                double dt = -tau_total * std::log(u);

                // 2. Дрейф у полі
                double vx_old = e.vx;
                e.vx += accel_x * dt;
                double vx_avg = 0.5 * (vx_old + e.vx);
                e.x += vx_avg * dt;

                double v_mag = std::sqrt(e.vx * e.vx + e.vy * e.vy + e.vz * e.vz);

                grand_total_path += v_mag * dt;
                grand_total_time += dt;
                grand_total_events++;

                // 3. Стохастичний вибір механізму
                if (dist_u(rng_) <= prob_phonon) {
                    phonon_events++;
                } else {
                    impurity_events++;
                }

                // 4. Ізотропне розсіювання швидкості
                double cos_th = 1.0 - 2.0 * dist_u(rng_);
                double sin_th = std::sqrt(std::max(0.0, 1.0 - cos_th * cos_th));
                double phi = 2.0 * std::numbers::pi * dist_u(rng_);

                e.vx = v_mag * sin_th * std::cos(phi);
                e.vy = v_mag * sin_th * std::sin(phi);
                e.vz = v_mag * cos_th;
            }
        }

        double sum_vx = 0.0;
        double sum_energy = 0.0;
        for (const auto& e : ensemble) {
            sum_vx += e.vx;
            double v_sq = e.vx * e.vx + e.vy * e.vy + e.vz * e.vz;
            sum_energy += (0.5 * m_eff_ * v_sq) / charge_e_;
        }

        return SimulationReport{
            .total_scatterings = grand_total_events,
            .phonon_scatterings = phonon_events,
            .impurity_scatterings = impurity_events,
            .mean_relaxation_time_s = grand_total_time / static_cast<double>(grand_total_events),
            .mean_free_path_nm = (grand_total_path / static_cast<double>(grand_total_events)) * 1e9,
            .drift_velocity_ms = sum_vx / static_cast<double>(cfg_.num_particles),
            .mean_energy_ev = sum_energy / static_cast<double>(cfg_.num_particles)
        };
    }

private:
    struct Electron {
        double x{0.0};
        double vx{0.0};
        double vy{0.0};
        double vz{0.0};
    };

    static constexpr double charge_e_{1.602176634e-19};
    static constexpr double mass_e0_{9.1093837015e-31};
    static constexpr double kb_joule_{1.380649e-23};

    Configuration cfg_;
    double m_eff_;
    std::mt19937 rng_;
};

int main() {
    CarrierMonteCarlo::Configuration config{};
    CarrierMonteCarlo solver(config);

    auto report = solver.execute();

    std::cout << std::scientific << std::setprecision(3);
    std::cout << "====================================================\n";
    std::cout << "     РЕЗУЛЬТАТИ СИМУЛЯЦІЇ МОНТЕ-КАРЛО (мова C++)\n";
    std::cout << "====================================================\n";
    std::cout << "Загальна кількість зіткнень:       " << report.total_scatterings << "\n";
    std::cout << "Актів фононного розсіювання:       " << report.phonon_scatterings << "\n";
    std::cout << "Актів домішкового розсіювання:     " << report.impurity_scatterings << "\n";
    std::cout << "----------------------------------------------------\n";
    std::cout << "Середній час релаксації tau:        " << report.mean_relaxation_time_s << " с\n";
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Довжина вільного пробігу lambda:   " << report.mean_free_path_nm << " нм\n";
    std::cout << std::scientific << std::setprecision(3);
    std::cout << "Середня дрейфова швидкість v_d:     " << report.drift_velocity_ms << " м/с\n";
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "Середня кінетична енергія <E>:     " << report.mean_energy_ev << " еВ\n";
    std::cout << "====================================================\n";

    return 0;
}
