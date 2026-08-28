// Simulation of gas particle entropy evolution in C++20 using RAII and standard algorithms
#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <numeric>
#include <iomanip>
#include <span>

struct Particle {
    double x{0.0};
    double y{0.0};
};

class GasSimulation {
public:
    GasSimulation(std::size_t num_particles, double grid_size)
        : grid_size_(grid_size),
          particles_(num_particles),
          rng_(1337)
    {
        init_particles();
    }

    void step(double step_size) {
        std::uniform_real_distribution<double> dist(-step_size, step_size);
        for (auto& p : particles_) {
            p.x += dist(rng_);
            p.y += dist(rng_);

            // Reflecting boundary conditions
            if (p.x < 0.0) p.x = -p.x;
            if (p.x >= grid_size_) p.x = 2.0 * grid_size_ - p.x - 1e-5;
            if (p.y < 0.0) p.y = -p.y;
            if (p.y >= grid_size_) p.y = 2.0 * grid_size_ - p.y - 1e-5;
        }
    }

    [[nodiscard]] double calculate_normalized_entropy(std::size_t grid_cells_side) const {
        const std::size_t total_cells = grid_cells_side * grid_cells_side;
        std::vector<std::size_t> counts(total_cells, 0);

        const double cell_width = grid_size_ / static_cast<double>(grid_cells_side);

        for (const auto& p : particles_) {
            auto cx = static_cast<std::size_t>(p.x / cell_width);
            auto cy = static_cast<std::size_t>(p.y / cell_width);
            cx = std::min(cx, grid_cells_side - 1);
            cy = std::min(cy, grid_cells_side - 1);

            counts[cy * grid_cells_side + cx]++;
        }

        const double n = static_cast<double>(particles_.size());
        double entropy = 0.0;

        for (auto count : counts) {
            if (count > 0) {
                const double p = static_cast<double>(count) / n;
                entropy -= p * std::log(p);
            }
        }

        const double max_entropy = std::log(static_cast<double>(total_cells));
        return entropy / max_entropy;
    }

private:
    void init_particles() {
        std::uniform_real_distribution<double> dist_x(0.0, grid_size_ / 2.0);
        std::uniform_real_distribution<double> dist_y(0.0, grid_size_);

        for (auto& p : particles_) {
            p.x = dist_x(rng_);
            p.y = dist_y(rng_);
        }
    }

    double grid_size_;
    std::vector<Particle> particles_;
    mutable std::mt19937 rng_;
};

int main() {
    constexpr std::size_t num_particles = 10000;
    constexpr double grid_size = 20.0;
    constexpr std::size_t grid_cells_side = 20;

    GasSimulation sim(num_particles, grid_size);

    std::cout << std::left << std::setw(8) << "Step" 
              << std::setw(25) << "Normalized Entropy (S / S_max)" << '\n';
    std::cout << std::string(35, '-') << '\n';

    for (int step = 0; step <= 100; step += 10) {
        std::cout << std::left << std::setw(8) << step 
                  << std::fixed << std::setprecision(6) 
                  << sim.calculate_normalized_entropy(grid_cells_side) << '\n';

        for (int sub = 0; sub < 10; ++sub) {
            sim.step(0.5);
        }
    }

    return 0;
}
