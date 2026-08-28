#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <iomanip>
#include <memory>
#include <numbers>

namespace SuperlatticeSim {

constexpr double HBAR = 1.054571817e-34;            // Дж·с
constexpr double ELEMENTARY_CHARGE = 1.602176634e-19; // Кл

struct Parameters {
    double period_d = 6.0e-9;        // Період суперґратки (м)
    double delta_joules = 50.0e-3 * ELEMENTARY_CHARGE; // Ширина мінізони (Дж)
    double tau_seconds = 0.5e-12;   // Час релаксації імпульсу (с)
    double dt = 1.0e-15;            // Крок часу (с)
    std::size_t num_particles = 1000;
    std::size_t total_steps = 20000;
};

class SuperlatticeSimulator {
private:
    Parameters params_;
    std::mt19937 rng_;
    std::uniform_real_distribution<double> dist_01_{0.0, 1.0};

    [[nodiscard]] double group_velocity(double kz) const noexcept {
        return (params_.delta_joules * params_.period_d / (2.0 * HBAR)) * std::sin(kz * params_.period_d);
    }

public:
    explicit SuperlatticeSimulator(const Parameters& params)
        : params_(params), rng_(1337) {}

    [[nodiscard]] double simulate_field(double F_dc) {
        std::vector<double> kz(params_.num_particles, 0.0);
        double p_coll = 1.0 - std::exp(-params_.dt / params_.tau_seconds);
        double dk_dt = -ELEMENTARY_CHARGE * F_dc / HBAR;
        double pi_d = std::numbers::pi / params_.period_d;

        double total_velocity_sum = 0.0;
        std::size_t sample_count = 0;

        for (std::size_t step = 0; step < params_.total_steps; ++step) {
            double step_v_sum = 0.0;

            for (auto& k : kz) {
                k += dk_dt * params_.dt;

                // Приведення до першої зони Бріллюена
                while (k > pi_d)  k -= 2.0 * pi_d;
                while (k < -pi_d) k += 2.0 * pi_d;

                // Стохастичне Монте-Карло розсіювання
                if (dist_01_(rng_) < p_coll) {
                    k = 0.0;
                }

                step_v_sum += group_velocity(k);
            }

            if (step >= params_.total_steps / 2) {
                total_velocity_sum += (step_v_sum / static_cast<double>(params_.num_particles));
                sample_count++;
            }
        }

        return total_velocity_sum / static_cast<double>(sample_count);
    }

    [[nodiscard]] double critical_field() const noexcept {
        return HBAR / (ELEMENTARY_CHARGE * params_.period_d * params_.tau_seconds);
    }

    [[nodiscard]] double peak_velocity() const noexcept {
        return (params_.delta_joules * params_.period_d) / (4.0 * HBAR);
    }
};

} // namespace SuperlatticeSim

int main() {
    SuperlatticeSim::Parameters params;
    SuperlatticeSim::SuperlatticeSimulator simulator(params);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Field_Vcm,DriftVel_cms,TheoryVel_cms\n";

    double F_c = simulator.critical_field();
    double v_max = simulator.peak_velocity();

    for (double F_kVcm = 0.5; F_kVcm <= 35.0; F_kVcm += 1.0) {
        double F_Vm = F_kVcm * 1.0e5;
        double v_sim = simulator.simulate_field(F_Vm);

        double f_ratio = F_Vm / F_c;
        double v_theory = v_max * (2.0 * f_ratio) / (1.0 + f_ratio * f_ratio);

        std::cout << F_kVcm << "," << (v_sim * 100.0) << "," << (v_theory * 100.0) << "\n";
    }

    return 0;
}
