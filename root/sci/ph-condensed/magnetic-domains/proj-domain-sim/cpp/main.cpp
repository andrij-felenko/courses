#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <string>
#include <memory>

class MagneticDomainSimulatorCPP {
private:
    std::size_t size_;
    double J_exchange_;
    double temperature_;
    std::vector<int> grid_;
    std::mt19937 rng_;

    [[nodiscard]] inline std::size_t idx(std::size_t r, std::size_t c) const noexcept {
        return r * size_ + c;
    }

public:
    MagneticDomainSimulatorCPP(std::size_t size, double J_exchange, double temperature)
        : size_(size), J_exchange_(J_exchange), temperature_(temperature),
          grid_(size * size), rng_(std::random_device{}()) 
    {
        std::uniform_int_distribution<int> dist(0, 1);
        for (auto& spin : grid_) {
            spin = dist(rng_) ? 1 : -1;
        }
    }

    void monte_carlo_step(double external_h = 0.0) {
        std::uniform_int_distribution<std::size_t> pos_dist(0, size_ - 1);
        std::uniform_real_distribution<double> prob_dist(0.0, 1.0);

        const std::size_t total_trials = size_ * size_;
        for (std::size_t k = 0; k < total_trials; ++k) {
            const std::size_t r = pos_dist(rng_);
            const std::size_t c = pos_dist(rng_);
            const int spin = grid_[idx(r, c)];

            const std::size_t top_r = (r == 0) ? (size_ - 1) : (r - 1);
            const std::size_t bot_r = (r == size_ - 1) ? 0 : (r + 1);
            const std::size_t left_c = (c == 0) ? (size_ - 1) : (c - 1);
            const std::size_t right_c = (c == size_ - 1) ? 0 : (c + 1);

            const int neighbors_sum = grid_[idx(top_r, c)] + grid_[idx(bot_r, c)] +
                                      grid_[idx(r, left_c)] + grid_[idx(r, right_c)];

            const double delta_energy = 2.0 * spin * (J_exchange_ * neighbors_sum + external_h);

            if (delta_energy <= 0.0 || prob_dist(rng_) < std::exp(-delta_energy / temperature_)) {
                grid_[idx(r, c)] = -spin;
            }
        }
    }

    [[nodiscard]] double magnetization() const noexcept {
        long long total_sum = 0;
        for (int spin : grid_) {
            total_sum += spin;
        }
        return static_cast<double>(total_sum) / static_cast<double>(grid_.size());
    }

    void render_ascii_map() const {
        std::cout << "=== C++ DOMAIN MAP ===\n";
        for (std::size_t r = 0; r < size_; ++r) {
            std::string line;
            line.reserve(size_);
            for (std::size_t c = 0; c < size_; ++c) {
                line.push_back(grid_[idx(r, c)] > 0 ? '#' : '.');
            }
            std::cout << line << '\n';
        }
    }
};

int main() {
    MagneticDomainSimulatorCPP sim(40, 1.0, 1.3);
    std::cout << "C++ Simulator M_init: " << sim.magnetization() << '\n';

    for (int step = 0; step < 120; ++step) {
        sim.monte_carlo_step(0.0);
    }

    std::cout << "C++ Simulator M_final: " << sim.magnetization() << '\n';
    sim.render_ascii_map();
    return 0;
}
