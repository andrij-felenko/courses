#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <iomanip>
#include <numeric>
#include <algorithm>

class MetropolisSimulator {
public:
    struct Stats {
        std::vector<double> probabilities;
        std::vector<std::vector<double>> transition_counts;
        std::vector<double> visit_counts;
        double max_imbalance{0.0};
    };

    MetropolisSimulator(std::vector<double> energies, double temperature)
        : energies_(std::move(energies)), temperature_(temperature), rng_(42) {}

    Stats run(size_t total_steps) {
        const size_t num_states = energies_.size();
        Stats stats;
        stats.visit_counts.assign(num_states, 0.0);
        stats.transition_counts.assign(num_states, std::vector<double>(num_states, 0.0));
        stats.probabilities.assign(num_states, 0.0);

        std::uniform_int_distribution<int> coin(0, 1);
        std::uniform_real_distribution<double> uniform(0.0, 1.0);

        size_t current_state = 0;

        for (size_t step = 0; step < total_steps; ++step) {
            stats.visit_counts[current_state] += 1.0;

            int dir = (coin(rng_) == 0) ? -1 : 1;
            size_t next_state = (current_state + dir + num_states) % num_states;

            double delta_e = energies_[next_state] - energies_[current_state];
            double accept_prob = (delta_e <= 0.0) ? 1.0 : std::exp(-delta_e / temperature_);

            if (uniform(rng_) < accept_prob) {
                stats.transition_counts[current_state][next_state] += 1.0;
                current_state = next_state;
            } else {
                stats.transition_counts[current_state][current_state] += 1.0;
            }
        }

        for (size_t i = 0; i < num_states; ++i) {
            stats.probabilities[i] = stats.visit_counts[i] / static_cast<double>(total_steps);
        }

        audit_detailed_balance(stats);
        return stats;
    }

private:
    void audit_detailed_balance(Stats& stats) const {
        const size_t num_states = energies_.size();
        stats.max_imbalance = 0.0;

        std::cout << "\n=== Аудит детального балансу C++ (T = " << temperature_ << ") ===\n";
        std::cout << std::fixed << std::setprecision(6);

        for (size_t i = 0; i < num_states; ++i) {
            for (size_t j = i + 1; j < num_states; ++j) {
                if (stats.visit_counts[i] == 0.0 || stats.visit_counts[j] == 0.0) continue;

                double w_ij = stats.transition_counts[i][j] / stats.visit_counts[i];
                double w_ji = stats.transition_counts[j][i] / stats.visit_counts[j];

                double flux_ij = stats.probabilities[i] * w_ij;
                double flux_ji = stats.probabilities[j] * w_ji;
                double imbalance = std::abs(flux_ij - flux_ji);

                stats.max_imbalance = std::max(stats.max_imbalance, imbalance);

                if (w_ij > 0.0 || w_ji > 0.0) {
                    std::cout << "  Ребро " << i << " <-> " << j
                              << " | P(i)*W(i->j): " << flux_ij
                              << " | P(j)*W(j->i): " << flux_ji
                              << " | Дисбаланс: " << imbalance << "\n";
                }
            }
        }
        std::cout << "Максимальний потік дисбалансу: " << stats.max_imbalance << "\n";
    }

    std::vector<double> energies_;
    double temperature_;
    std::mt19937 rng_;
};

int main() {
    std::vector<double> energy_levels = {4.0, 1.0, 0.0, 2.5, 3.0, 0.5, 1.5, 5.0};
    MetropolisSimulator sim(energy_levels, 1.5);
    auto stats = sim.run(10'000'000);

    return 0;
}
