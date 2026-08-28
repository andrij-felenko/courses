#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <numeric>
#include <iomanip>

class TunnelingSimulator {
public:
    using Complex = std::complex<double>;

    struct Config {
        std::size_t grid_points{256};
        double domain_length{100.0};
        double dt{0.05};
        std::size_t time_steps{400};
        double mass{1.0};
        double hbar{1.0};
        double barrier_x1{48.0};
        double barrier_x2{52.0};
        double barrier_height{1.5};
        double packet_x0{25.0};
        double packet_sigma{4.0};
        double packet_energy{1.0};
    };

    explicit TunnelingSimulator(Config cfg)
        : config_(cfg),
          dx_(cfg.domain_length / static_cast<double>(cfg.grid_points)),
          psi_(cfg.grid_points),
          potential_(cfg.grid_points) {
        initialize();
    }

    void run() {
        std::vector<Complex> psi_k(config_.grid_points);

        for (std::size_t step = 0; step < config_.time_steps; ++step) {
            // 1. Половина кроку потенціалу
            apply_potential_half_step();

            // 2. Перехід в імпульсний простір
            dft(psi_, psi_k, 1);

            // 3. Оператор кінетичної енергії
            apply_kinetic_step(psi_k);

            // 4. Зворотне перетворення в координатний простір
            dft(psi_k, psi_, -1);

            // 5. Половина кроку потенціалу
            apply_potential_half_step();
        }
    }

    [[nodiscard]] std::pair<double, double> calculate_coefficients() const {
        double reflection = 0.0;
        double transmission = 0.0;

        for (std::size_t i = 0; i < config_.grid_points; ++i) {
            const double x = static_cast<double>(i) * dx_;
            const double prob = std::norm(psi_[i]) * dx_;
            if (x < config_.barrier_x1) {
                reflection += prob;
            } else if (x > config_.barrier_x2) {
                transmission += prob;
            }
        }
        return {reflection, transmission};
    }

private:
    void initialize() {
        const double k0 = std::sqrt(2.0 * config_.mass * config_.packet_energy) / config_.hbar;
        const double norm = 1.0 / std::sqrt(config_.packet_sigma * std::sqrt(std::numbers::pi));

        for (std::size_t i = 0; i < config_.grid_points; ++i) {
            const double x = static_cast<double>(i) * dx_;
            potential_[i] = (x >= config_.barrier_x1 && x <= config_.barrier_x2)
                                ? config_.barrier_height
                                : 0.0;

            const double gaussian = std::exp(-std::pow(x - config_.packet_x0, 2) /
                                             (2.0 * std::pow(config_.packet_sigma, 2)));
            psi_[i] = norm * gaussian * std::exp(Complex(0.0, k0 * x));
        }
    }

    void apply_potential_half_step() {
        for (std::size_t i = 0; i < config_.grid_points; ++i) {
            const double phase = -potential_[i] * config_.dt / (2.0 * config_.hbar);
            psi_[i] *= std::exp(Complex(0.0, phase));
        }
    }

    void apply_kinetic_step(std::vector<Complex>& psi_k) const {
        const std::size_t n = config_.grid_points;
        for (std::size_t k = 0; k < n; ++k) {
            const double k_val = (k < n / 2)
                                     ? (2.0 * std::numbers::pi * static_cast<double>(k) / config_.domain_length)
                                     : (2.0 * std::numbers::pi * static_cast<double>(static_cast<long long>(k) - static_cast<long long>(n)) / config_.domain_length);
            const double phase = -(config_.hbar * k_val * k_val / (2.0 * config_.mass)) * config_.dt;
            psi_k[k] *= std::exp(Complex(0.0, phase));
        }
    }

    void dft(const std::vector<Complex>& in, std::vector<Complex>& out, int sign) const {
        const std::size_t n = in.size();
        for (std::size_t k = 0; k < n; ++k) {
            out[k] = Complex(0.0, 0.0);
            for (std::size_t i = 0; i < n; ++i) {
                const double angle = static_cast<double>(sign) * 2.0 * std::numbers::pi * static_cast<double>(k * i) / static_cast<double>(n);
                out[k] += in[i] * std::exp(Complex(0.0, angle));
            }
            if (sign < 0) {
                out[k] /= static_cast<double>(n);
            }
        }
    }

    Config config_;
    double dx_;
    std::vector<Complex> psi_;
    std::vector<double> potential_;
};

int main() {
    TunnelingSimulator::Config config;
    TunnelingSimulator sim(config);
    sim.run();

    const auto [R, T] = sim.calculate_coefficients();

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=== Результати чисельного симулятора тунелювання (C++) ===\n";
    std::cout << "Енергія пакета E0: " << config.packet_energy
              << " | Висота бар'єра V0: " << config.barrier_height << "\n";
    std::cout << "Коефіцієнт відбивання R: " << R << "\n";
    std::cout << "Коефіцієнт проходження (тунелювання) T: " << T << "\n";
    std::cout << "Сума ймовірностей R + T: " << R + T << "\n";

    return 0;
}
