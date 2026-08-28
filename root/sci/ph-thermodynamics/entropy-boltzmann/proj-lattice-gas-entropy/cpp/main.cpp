#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <iomanip>
#include <memory>

struct Particle {
    int x;
    int y;
};

class LatticeGasSimulation {
public:
    LatticeGasSimulation(int lx, int ly, int num_particles)
        : lx_(lx), ly_(ly), num_particles_(num_particles),
          gen_(std::random_device{}()), dis_(0, 3) {
        
        particles_.reserve(num_particles);
        std::uniform_int_distribution<int> dis_x(0, lx / 2 - 1);
        std::uniform_int_distribution<int> dis_y(0, ly - 1);

        for (int i = 0; i < num_particles; ++i) {
            particles_.push_back({dis_x(gen_), dis_y(gen_)});
        }
    }

    void step() {
        for (auto& p : particles_) {
            int dir = dis_(gen_);
            int nx = p.x;
            int ny = p.y;

            switch (dir) {
                case 0: nx++; break; // праворуч
                case 1: nx--; break; // ліворуч
                case 2: ny++; break; // вгору
                case 3: ny--; break; // вниз
            }

            if (nx >= 0 && nx < lx_) p.x = nx;
            if (ny >= 0 && ny < ly_) p.y = ny;
        }
    }

    [[nodiscard]] int count_left() const noexcept {
        int count = 0;
        int half_x = lx_ / 2;
        for (const auto& p : particles_) {
            if (p.x < half_x) ++count;
        }
        return count;
    }

    [[nodiscard]] double calculate_entropy() const noexcept {
        int n_left = count_left();
        int n_right = num_particles_ - n_left;

        double log_n_fact = std::lgamma(num_particles_ + 1.0);
        double log_nl_fact = std::lgamma(n_left + 1.0);
        double log_nr_fact = std::lgamma(n_right + 1.0);

        return log_n_fact - log_nl_fact - log_nr_fact;
    }

    [[nodiscard]] int total_particles() const noexcept { return num_particles_; }

private:
    int lx_;
    int ly_;
    int num_particles_;
    std::vector<Particle> particles_;
    mutable std::mt19937 gen_;
    mutable std::uniform_int_distribution<int> dis_;
};

int main() {
    constexpr int LX = 100;
    constexpr int LY = 100;
    constexpr int N = 1000;
    constexpr int TOTAL_STEPS = 200;
    constexpr int INTERVAL = 10;

    auto sim = std::make_unique<LatticeGasSimulation>(LX, LY, N);

    std::cout << std::left 
              << std::setw(8) << "Крок" 
              << std::setw(8) << "N_L" 
              << std::setw(8) << "N_R" 
              << std::setw(14) << "S/k_B" 
              << std::setw(14) << "S_max/k_B" << "\n";
    std::cout << std::string(52, '-') << "\n";

    double s_max = N * std::log(2.0);

    for (int step = 0; step <= TOTAL_STEPS; step += INTERVAL) {
        int n_left = sim->count_left();
        int n_right = N - n_left;
        double s_boltzmann = sim->calculate_entropy();

        std::cout << std::left 
                  << std::setw(8) << step 
                  << std::setw(8) << n_left 
                  << std::setw(8) << n_right 
                  << std::setw(14) << std::fixed << std::setprecision(4) << s_boltzmann 
                  << std::setw(14) << std::fixed << std::setprecision(4) << s_max << "\n";

        for (int k = 0; k < INTERVAL; ++k) {
            sim->step();
        }
    }

    return 0;
}
