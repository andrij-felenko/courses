// Simulation of Ion Implantation via Monte Carlo (Idiomatic C++20)
#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <numbers>
#include <iomanip>
#include <memory>
#include <numeric>

namespace ion_sim {

constexpr double SI_DENSITY = 5.02e22;      // Atom density of Si (atoms/cm^3)
constexpr double LAMBDA_STEP = 2.5e-8;      // Free path step (cm)
constexpr double E_DISPLACEMENT = 15.0;     // Threshold displacement energy (eV)
constexpr double E_SURFACE_BIND = 4.7;      // Surface binding energy for Si sputtering (eV)

struct IonState {
    double energy_ev{0.0};
    double x_cm{0.0};
    double y_cm{0.0};
    double dir_x{1.0};
    double dir_y{0.0};
    bool is_recoil{false};
};

struct SimConfig {
    double initial_energy_ev{50000.0}; // 50 keV
    double m1_amu{11.0};               // Boron
    double z1{5.0};
    double m2_amu{28.08};              // Silicon
    double z2{14.0};
    double ke_coeff{1.2e6};            // Electronic drag coefficient
    std::size_t total_ions{10000};
    double depth_max_cm{400e-7};       // 400 nm depth window
    std::size_t num_bins{100};
};

class ImplantationSimulator {
public:
    explicit ImplantationSimulator(SimConfig config)
        : config_(config),
          rng_(42),
          dist_distrib_(0.0, 1.0),
          vacancies_hist_(config.num_bins, 0),
          range_hist_(config.num_bins, 0),
          sputtered_count_(0) {}

    void run() {
        for (std::size_t i = 0; i < config_.total_ions; ++i) {
            simulate_single_ion();
        }
    }

    void print_results() const {
        std::cout << "=== Monte Carlo Ion Stopping Profile (C++20) ===\n";
        std::cout << "Simulated Primary Ions: " << config_.total_ions << "\n";
        std::cout << "Sputtered Surface Silicon Atoms: " << sputtered_count_ << "\n";
        std::cout << std::setw(12) << "Depth (nm)"
                  << std::setw(18) << "Ion Concentration"
                  << std::setw(24) << "Vacancy Cascade\n";

        for (std::size_t i = 0; i < config_.num_bins; i += 10) {
            double depth_nm = (i + 0.5) * (config_.depth_max_cm * 1e7 / config_.num_bins);
            std::cout << std::setw(12) << std::fixed << std::setprecision(1) << depth_nm
                      << std::setw(18) << range_hist_[i]
                      << std::setw(24) << vacancies_hist_[i] << "\n";
        }
    }

    [[nodiscard]] double calculate_projected_range_nm() const {
        double weighted_sum = 0.0;
        std::size_t total_stops = 0;
        for (std::size_t i = 0; i < config_.num_bins; ++i) {
            double depth_nm = (i + 0.5) * (config_.depth_max_cm * 1e7 / config_.num_bins);
            weighted_sum += depth_nm * range_hist_[i];
            total_stops += range_hist_[i];
        }
        return total_stops > 0 ? weighted_sum / total_stops : 0.0;
    }

    [[nodiscard]] double calculate_straggling_nm(double r_p_nm) const {
        double weighted_sq_sum = 0.0;
        std::size_t total_stops = 0;
        for (std::size_t i = 0; i < config_.num_bins; ++i) {
            double depth_nm = (i + 0.5) * (config_.depth_max_cm * 1e7 / config_.num_bins);
            double diff = depth_nm - r_p_nm;
            weighted_sq_sum += diff * diff * range_hist_[i];
            total_stops += range_hist_[i];
        }
        return total_stops > 0 ? std::sqrt(weighted_sq_sum / total_stops) : 0.0;
    }

private:
    void simulate_recoil_cascade(double start_x, double start_y, double start_energy) {
        if (start_energy < E_DISPLACEMENT) return;

        IonState recoil{
            .energy_ev = start_energy - E_DISPLACEMENT,
            .x_cm = start_x,
            .y_cm = start_y,
            .dir_x = (dist_distrib_(rng_) - 0.5) * 2.0,
            .dir_y = (dist_distrib_(rng_) - 0.5) * 2.0,
            .is_recoil = true
        };

        const double max_b = 1.5e-8;
        while (recoil.energy_ev > E_DISPLACEMENT && recoil.x_cm >= 0.0 && recoil.x_cm < config_.depth_max_cm) {
            const double dE_elec = config_.ke_coeff * std::sqrt(recoil.energy_ev) * LAMBDA_STEP;
            recoil.energy_ev -= dE_elec;
            if (recoil.energy_ev <= 0.0) break;

            const double r = dist_distrib_(rng_);
            const double b = std::sqrt(r) * max_b;
            const double sin_half_theta = 1.0 / std::sqrt(1.0 + (b * b * 1e16) * (recoil.energy_ev / 500.0));
            const double T_transferred = recoil.energy_ev * (sin_half_theta * sin_half_theta);

            if (T_transferred > E_DISPLACEMENT) {
                const auto bin = static_cast<std::size_t>((recoil.x_cm / config_.depth_max_cm) * config_.num_bins);
                if (bin < config_.num_bins) {
                    vacancies_hist_[bin]++;
                }
                if (T_transferred > 50.0) {
                    simulate_recoil_cascade(recoil.x_cm, recoil.y_cm, T_transferred);
                }
            }

            recoil.energy_ev -= T_transferred;
            recoil.x_cm += recoil.dir_x * LAMBDA_STEP;
            recoil.y_cm += recoil.dir_y * LAMBDA_STEP;
        }
    }

    void simulate_single_ion() {
        IonState ion{.energy_ev = config_.initial_energy_ev, .x_cm = 0.0, .y_cm = 0.0, .dir_x = 1.0, .dir_y = 0.0, .is_recoil = false};

        const double max_b = 1.5e-8;
        const double t_max_factor = (4.0 * config_.m1_amu * config_.m2_amu) /
                                    ((config_.m1_amu + config_.m2_amu) * (config_.m1_amu + config_.m2_amu));

        while (ion.energy_ev > 5.0 && ion.x_cm >= 0.0 && ion.x_cm < config_.depth_max_cm) {
            // 1. Electronic drag loss
            const double dE_elec = config_.ke_coeff * std::sqrt(ion.energy_ev) * LAMBDA_STEP;
            ion.energy_ev -= dE_elec;
            if (ion.energy_ev <= 0.0) break;

            // 2. Impact parameter & nuclear collision
            const double r = dist_distrib_(rng_);
            const double b = std::sqrt(r) * max_b;

            const double sin_half_theta = 1.0 / std::sqrt(1.0 + (b * b * 1e16) * (ion.energy_ev / 1000.0));
            const double T_transferred = t_max_factor * ion.energy_ev * (sin_half_theta * sin_half_theta);

            // 3. Frenkel pair vacancy count & recoil cascade
            if (T_transferred > E_DISPLACEMENT) {
                const auto bin = static_cast<std::size_t>((ion.x_cm / config_.depth_max_cm) * config_.num_bins);
                if (bin < config_.num_bins) {
                    vacancies_hist_[bin]++;
                }
                if (ion.x_cm < 1.0e-7 && T_transferred > E_SURFACE_BIND) {
                    sputtered_count_++;
                }
                if (T_transferred > 100.0) {
                    simulate_recoil_cascade(ion.x_cm, ion.y_cm, T_transferred);
                }
            }

            ion.energy_ev -= T_transferred;

            // 4. Direction update
            const double theta_lab = sin_half_theta * (config_.m2_amu / (config_.m1_amu + config_.m2_amu));
            const double phi = (dist_distrib_(rng_) - 0.5) * 2.0 * theta_lab;

            const double new_dir_x = ion.dir_x * std::cos(phi) - ion.dir_y * std::sin(phi);
            const double new_dir_y = ion.dir_x * std::sin(phi) + ion.dir_y * std::cos(phi);
            const double norm = std::hypot(new_dir_x, new_dir_y);

            ion.dir_x = new_dir_x / norm;
            ion.dir_y = new_dir_y / norm;

            ion.x_cm += ion.dir_x * LAMBDA_STEP;
            ion.y_cm += ion.dir_y * LAMBDA_STEP;
        }

        if (ion.x_cm >= 0.0 && ion.x_cm < config_.depth_max_cm) {
            const auto bin = static_cast<std::size_t>((ion.x_cm / config_.depth_max_cm) * config_.num_bins);
            if (bin < config_.num_bins) {
                range_hist_[bin]++;
            }
        }
    }

    SimConfig config_;
    std::mt19937 rng_;
    std::uniform_real_distribution<double> dist_distrib_;
    std::vector<int> vacancies_hist_;
    std::vector<int> range_hist_;
    std::size_t sputtered_count_{0};
};

} // namespace ion_sim

int main() {
    ion_sim::SimConfig config;
    ion_sim::ImplantationSimulator sim(config);
    sim.run();
    sim.print_results();
    double r_p = sim.calculate_projected_range_nm();
    double delta_r_p = sim.calculate_straggling_nm(r_p);
    std::cout << "Mean Projected Range R_p: " << std::fixed << std::setprecision(2)
              << r_p << " nm\n";
    std::cout << "Calculated Straggling Delta R_p: " << std::fixed << std::setprecision(2)
              << delta_r_p << " nm\n";
    return 0;
}
