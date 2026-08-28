#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <numbers>
#include <iomanip>

struct Electron {
    double vx{0.0};
    double vy{0.0};
    double vz{0.0};
};

struct SimulationConfig {
    std::size_t num_electrons{50'000};
    std::size_t num_steps{20'000};
    double dt{1.0e-16};           // 0.1 фс
    double tau{2.5e-14};          // 25 фс
    double e_field{1.0e4};        // 10 кВ/м
    double concentration{8.5e28}; // 8.5e28 м^-3 (Мідь)
    double temperature{300.0};    // 300 К
};

class DrudeSimulation {
public:
    explicit DrudeSimulation(SimulationConfig config)
        : cfg_{config},
          rng_{std::random_device{}()},
          dist_uniform_{0.0, 1.0}
    {
        const double sigma_v = std::sqrt(kBoltzmann * cfg_.temperature / kElecMass);
        dist_normal_ = std::normal_distribution<double>{0.0, sigma_v};

        electrons_.resize(cfg_.num_electrons);
        for (auto& el : electrons_) {
            el.vx = dist_normal_(rng_);
            el.vy = dist_normal_(rng_);
            el.vz = dist_normal_(rng_);
        }
    }

    struct Results {
        double vd_sim;
        double vd_theory;
        double current_density;
        double conductivity_sim;
        double conductivity_theory;
        double mobility;
        double diffusion_coeff;
        double einstein_ratio;
    };

    Results run() {
        const double acc_x = - (kElecCharge * cfg_.e_field) / kElecMass;
        const double p_coll = 1.0 - std::exp(-cfg_.dt / cfg_.tau);

        double total_vd_sum{0.0};
        std::size_t sample_count{0};

        for (std::size_t step = 0; step < cfg_.num_steps; ++step) {
            double step_vx_sum{0.0};

            for (auto& el : electrons_) {
                el.vx += acc_x * cfg_.dt;

                if (dist_uniform_(rng_) < p_coll) {
                    el.vx = dist_normal_(rng_);
                    el.vy = dist_normal_(rng_);
                    el.vz = dist_normal_(rng_);
                }

                step_vx_sum += el.vx;
            }

            // Накопичення середнього після завершення перехідного процесу (після 20% кроків)
            if (step > cfg_.num_steps / 5) {
                total_vd_sum += (step_vx_sum / static_cast<double>(cfg_.num_electrons));
                ++sample_count;
            }
        }

        const double mean_vd_sim = total_vd_sum / static_cast<double>(sample_count);
        const double mean_vd_theory = - (kElecCharge * cfg_.tau / kElecMass) * cfg_.e_field;
        const double j_sim = - cfg_.concentration * kElecCharge * mean_vd_sim;
        const double sigma_sim = j_sim / cfg_.e_field;
        const double sigma_theory = (cfg_.concentration * kElecCharge * kElecCharge * cfg_.tau) / kElecMass;
        const double mobility = std::abs(mean_vd_sim) / cfg_.e_field;
        const double diff_coeff = (kBoltzmann * cfg_.temperature / kElecMass) * cfg_.tau;
        const double einstein = diff_coeff / mobility;

        return {mean_vd_sim, mean_vd_theory, j_sim, sigma_sim, sigma_theory, mobility, diff_coeff, einstein};
    }

private:
    static constexpr double kElecCharge{1.602176634e-19};
    static constexpr double kElecMass{9.1093837015e-31};
    static constexpr double kBoltzmann{1.380649e-23};

    SimulationConfig cfg_;
    std::vector<Electron> electrons_;
    std::mt19937_64 rng_;
    std::uniform_real_distribution<double> dist_uniform_;
    std::normal_distribution<double> dist_normal_;
};

int main() {
    DrudeSimulation sim(SimulationConfig{});
    const auto res = sim.run();

    std::cout << std::scientific << std::setprecision(4);
    std::cout << "=== Результати Монте-Карло симуляції моделі Друде ===\n";
    std::cout << "Дрейфова швидкість (симуляція): " << std::setw(12) << res.vd_sim << " м/с\n";
    std::cout << "Дрейфова швидкість (теорія):    " << std::setw(12) << res.vd_theory << " м/с\n";
    std::cout << "Густина струму j (симуляція):   " << std::setw(12) << res.current_density << " А/м²\n";
    std::cout << "Питома провідність σ (симул.):  " << std::setw(12) << res.conductivity_sim << " См/м\n";
    std::cout << "Питома провідність σ (теорія):  " << std::setw(12) << res.conductivity_theory << " См/м\n";
    std::cout << "Питомий опір ρ (симуляція):     " << std::setw(12) << (1.0 / res.conductivity_sim) << " Ом·м\n";
    std::cout << "Рухливість електронів μ:        " << std::setw(12) << res.mobility << " м²/(В·с)\n";
    std::cout << "Коефіцієнт дифузії D (теорія):  " << std::setw(12) << res.diffusion_coeff << " м²/с\n";
    std::cout << "Співвідношення Ейнштейна D/μ:   " << std::setw(12) << res.einstein_ratio << " В (теорія kBT/e: 2.5852e-02 В)\n";

    return 0;
}
