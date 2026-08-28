#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <memory>
#include <iomanip>
#include <span>

class CahnHilliardSolver2D {
public:
    struct Config {
        std::size_t grid_size{128};
        double dt{0.02};
        double dx{1.0};
        double kappa{1.0};
        double mobility{1.0};
        std::size_t steps_to_run{5000};
    };

    explicit CahnHilliardSolver2D(Config cfg)
        : config_(cfg),
          c_(cfg.grid_size * cfg.grid_size, 0.0),
          mu_(cfg.grid_size * cfg.grid_size, 0.0),
          c_next_(cfg.grid_size * cfg.grid_size, 0.0) {}

    void initialize_uniform(double mean_composition, double noise_amplitude = 0.1) {
        std::mt19937 rng(1337);
        std::uniform_real_distribution<double> dist(-noise_amplitude / 2.0, noise_amplitude / 2.0);

        for (auto& val : c_) {
            val = mean_composition + dist(rng);
        }
    }

    void step() {
        const auto N = config_.grid_size;
        const auto h2 = config_.dx * config_.dx;

        // 1. Етап обчислення хімічного потенціалу μ
        for (std::size_t i = 0; i < N; ++i) {
            for (std::size_t j = 0; j < N; ++j) {
                const auto idx = index(i, j);
                const double val = c_[idx];
                const double df_dc = val * val * val - val;
                const double lap_c = compute_laplacian(c_, i, j, h2);
                mu_[idx] = df_dc - config_.kappa * lap_c;
            }
        }

        // 2. Етап оновлення поля концентрації c^(n+1)
        for (std::size_t i = 0; i < N; ++i) {
            for (std::size_t j = 0; j < N; ++j) {
                const auto idx = index(i, j);
                const double lap_mu = compute_laplacian(mu_, i, j, h2);
                c_next_[idx] = c_[idx] + config_.dt * config_.mobility * lap_mu;
            }
        }

        c_.swap(c_next_);
    }

    [[nodiscard]] double compute_total_free_energy() const {
        const auto N = config_.grid_size;
        const auto h = config_.dx;
        double total_energy = 0.0;

        for (std::size_t i = 0; i < N; ++i) {
            for (std::size_t j = 0; j < N; ++j) {
                const double val = c_[index(i, j)];
                const double f_bulk = 0.25 * std::pow(val, 4) - 0.5 * std::pow(val, 2);

                const std::size_t i_next = (i + 1) % N;
                const std::size_t i_prev = (i + N - 1) % N;
                const std::size_t j_next = (j + 1) % N;
                const std::size_t j_prev = (j + N - 1) % N;

                const double dc_dx = (c_[index(i_next, j)] - c_[index(i_prev, j)]) / (2.0 * h);
                const double dc_dy = (c_[index(i, j_next)] - c_[index(i, j_prev)]) / (2.0 * h);
                const double grad_sq = dc_dx * dc_dx + dc_dy * dc_dy;

                total_energy += f_bulk + 0.5 * config_.kappa * grad_sq;
            }
        }

        return total_energy * (h * h);
    }

    [[nodiscard]] std::span<const double> get_composition_field() const noexcept {
        return c_;
    }

private:
    [[nodiscard]] constexpr std::size_t index(std::size_t i, std::size_t j) const noexcept {
        return i * config_.grid_size + j;
    }

    [[nodiscard]] double compute_laplacian(std::span<const double> field, 
                                           std::size_t i, std::size_t j, 
                                           double h2) const noexcept {
        const auto N = config_.grid_size;
        const std::size_t i_next = (i + 1) % N;
        const std::size_t i_prev = (i + N - 1) % N;
        const std::size_t j_next = (j + 1) % N;
        const std::size_t j_prev = (j + N - 1) % N;

        const double center = field[index(i, j)];
        const double left   = field[index(i_prev, j)];
        const double right  = field[index(i_next, j)];
        const double up     = field[index(i, j_prev)];
        const double down   = field[index(i, j_next)];

        return (left + right + up + down - 4.0 * center) / h2;
    }

    Config config_;
    std::vector<double> c_;
    std::vector<double> mu_;
    std::vector<double> c_next_;
};

int main() {
    CahnHilliardSolver2D::Config cfg{.grid_size = 128, .dt = 0.02, .steps_to_run = 5000};
    CahnHilliardSolver2D solver(cfg);

    solver.initialize_uniform(0.0);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Початкова вільна енергія F: " << solver.compute_total_free_energy() << "\n";

    constexpr std::size_t total_steps = 5000;
    for (std::size_t step = 1; step <= total_steps; ++step) {
        solver.step();
        if (step % 1000 == 0) {
            std::cout << "Крок " << std::setw(5) << step 
                      << " | Повна вільна енергія F: " << solver.compute_total_free_energy() << "\n";
        }
    }

    std::cout << "Симуляцію 2D спінодального розпаду на C++ завершено успішно.\n";
    return 0;
}
