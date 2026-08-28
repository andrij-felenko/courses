#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <iomanip>
#include <numeric>
#include <algorithm>

class RadioactiveDecaySimulator {
public:
    struct SimulationPoint {
        double time_s;
        size_t n_simulated;
        double n_analytical;
        double relative_error_pct;
    };

    RadioactiveDecaySimulator(double half_life_s, size_t initial_nuclei)
        : half_life_(half_life_s),
          n0_(initial_nuclei),
          lambda_(std::log(2.0) / half_life_s),
          rng_(std::random_device{}()) {}

    [[nodiscard]] std::vector<SimulationPoint> run(double total_time_s, double dt_s) {
        const double p_decay = 1.0 - std::exp(-lambda_ * dt_s);
        std::bernoulli_distribution dist(p_decay);

        std::vector<SimulationPoint> results;
        size_t current_n = n0_;
        double current_time = 0.0;

        const size_t total_steps = static_cast<size_t>(total_time_s / dt_s);

        for (size_t step = 0; step <= total_steps; ++step) {
            const double analytic_n = n0_ * std::exp(-lambda_ * current_time);
            const double err_pct = (analytic_n > 0.0) 
                ? std::abs(static_cast<double>(current_n) - analytic_n) / analytic_n * 100.0 
                : 0.0;

            results.push_back({current_time, current_n, analytic_n, err_pct});

            // Симуляція кроку: розпад для кожного з n ядер
            size_t decayed_count = 0;
            for (size_t i = 0; i < current_n; ++i) {
                if (dist(rng_)) {
                    ++decayed_count;
                }
            }
            current_n -= decayed_count;
            current_time += dt_s;
        }

        return results;
    }

    // Обчислення флуктуацій та перевірка закону 1/sqrt(N)
    [[nodiscard]] static double compute_statistical_fluctuation(
        size_t num_runs, size_t nuclei_count, double half_life_s, double observation_time_s) {
        
        const double lambda = std::log(2.0) / half_life_s;
        const double p_decay_total = 1.0 - std::exp(-lambda * observation_time_s);

        std::mt19937 generator(42); // Фіксоване зерно для відтворюваності
        std::binomial_distribution<size_t> binom(nuclei_count, p_decay_total);

        std::vector<double> decay_counts(num_runs);
        for (size_t i = 0; i < num_runs; ++i) {
            decay_counts[i] = static_cast<double>(binom(generator));
        }

        const double mean = std::accumulate(decay_counts.begin(), decay_counts.end(), 0.0) / num_runs;
        double variance = 0.0;
        for (double val : decay_counts) {
            variance += (val - mean) * (val - mean);
        }
        variance /= (num_runs - 1);

        return std::sqrt(variance) / mean; // Відносне стандартне відхилення
    }

private:
    double half_life_;
    size_t n0_;
    double lambda_;
    std::mt19937 rng_;
};

int main() {
    constexpr double half_life = 2.0;
    constexpr size_t n0 = 100'000;
    constexpr double dt = 0.1;
    constexpr double total_time = 5.0;

    RadioactiveDecaySimulator sim(half_life, n0);
    const auto timeline = sim.run(total_time, dt);

    std::cout << "=== Симуляція Монте-Карло радіоактивного розпаду (C++) ===\n";
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "t (с) | Симуляція N(t) | Аналітичне N(t) | Похибка (%)\n";
    std::cout << "----------------------------------------------------\n";

    for (size_t i = 0; i < timeline.size(); i += 5) {
        const auto& pt = timeline[i];
        std::cout << std::setw(5) << pt.time_s << " | "
                  << std::setw(14) << pt.n_simulated << " | "
                  << std::setw(15) << pt.n_analytical << " | "
                  << std::setw(10) << std::setprecision(3) << pt.relative_error_pct << "\n";
    }

    // Демонстрація масштабування похибки 1/sqrt(N)
    std::cout << "\n=== Статистичні флуктуації (Закон 1/sqrt(N)) ===\n";
    for (size_t sample_N : {100, 1000, 10000, 100000}) {
        const double rel_stddev = RadioactiveDecaySimulator::compute_statistical_fluctuation(
            1000, sample_N, 2.0, 1.0);
        const double theoretical_rel_stddev = 1.0 / std::sqrt(sample_N * (1.0 - std::exp(-std::log(2.0)/2.0 * 1.0)));
        std::cout << "N0 = " << std::setw(6) << sample_N 
                  << " | Експериментальне σ/N = " << std::setw(6) << std::setprecision(4) << rel_stddev
                  << " | Теоретичне 1/√<N> = " << std::setw(6) << theoretical_rel_stddev << "\n";
    }

    return 0;
}
