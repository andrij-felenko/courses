#include <iostream>
#include <vector>
#include <array>
#include <random>
#include <numeric>
#include <cmath>
#include <iomanip>
#include <span>

constexpr size_t NUM_USERS = 4;
constexpr size_t CHIP_LEN = 64;
constexpr size_t NUM_BITS = 10000;

class WalshGenerator {
public:
    static auto generate(size_t n) -> std::vector<std::vector<int>> {
        std::vector<std::vector<int>> matrix(n, std::vector<int>(n, 0));
        matrix[0][0] = 1;
        for (size_t len = 1; len < n; len *= 2) {
            for (size_t i = 0; i < len; ++i) {
                for (size_t j = 0; j < len; ++j) {
                    matrix[i + len][j] = matrix[i][j];
                    matrix[i][j + len] = matrix[i][j];
                    matrix[i + len][j + len] = -matrix[i][j];
                }
            }
        }
        return matrix;
    }
};

class DsssSimulation {
private:
    std::vector<std::vector<int>> walsh_matrix_;
    std::mt19937 rng_;
    std::uniform_int_distribution<int> bit_dist_{0, 1};

public:
    DsssSimulation() 
        : walsh_matrix_(WalshGenerator::generate(CHIP_LEN)),
          rng_(std::random_device{}()) {}

    auto run_point(double eb_n0_db) -> double {
        const double eb_n0_linear = std::pow(10.0, eb_n0_db / 10.0);
        const double noise_variance = static_cast<double>(CHIP_LEN) / (2.0 * eb_n0_linear);
        const double noise_std_dev = std::sqrt(noise_variance);

        std::normal_distribution<double> noise_dist(0.0, noise_std_dev);
        std::array<size_t, NUM_USERS> errors = {0};

        std::array<int, NUM_USERS> tx_bits;
        std::array<double, CHIP_LEN> composite_tx;
        std::array<double, CHIP_LEN> composite_rx;

        for (size_t b = 0; b < NUM_BITS; ++b) {
            composite_tx.fill(0.0);

            // Крок 1 і 2: Spreading (множення біта на рядок матриці Волша)
            for (size_t u = 0; u < NUM_USERS; ++u) {
                tx_bits[u] = (bit_dist_(rng_) == 0) ? 1 : -1;
                for (size_t c = 0; c < CHIP_LEN; ++c) {
                    composite_tx[c] += tx_bits[u] * walsh_matrix_[u][c];
                }
            }

            // Крок 3: Додавання шуму AWGN у каналі
            for (size_t c = 0; c < CHIP_LEN; ++c) {
                composite_rx[c] = composite_tx[c] + noise_dist(rng_);
            }

            // Крок 4: Despreading (кореляційний інтегратор)
            for (size_t u = 0; u < NUM_USERS; ++u) {
                double correlator_output = 0.0;
                for (size_t c = 0; c < CHIP_LEN; ++c) {
                    correlator_output += composite_rx[c] * walsh_matrix_[u][c];
                }

                const int rx_decision = (correlator_output >= 0.0) ? 1 : -1;
                if (rx_decision != tx_bits[u]) {
                    ++errors[u];
                }
            }
        }

        const size_t total_errors = std::accumulate(errors.begin(), errors.end(), size_t{0});
        return static_cast<double>(total_errors) / static_cast<double>(NUM_BITS * NUM_USERS);
    }
};

int main() {
    std::cout << "=== Моделювання DSSS CDMA (Modern C++20) ===\n";
    std::cout << "Кількість користувачів: " << NUM_USERS 
              << ", Довжина коду Волша: " << CHIP_LEN << " чипів\n";
    std::cout << "Кількість переданих бітів: " << NUM_BITS << " на абонента\n\n";

    DsssSimulation sim;
    const std::vector<double> snr_values = {-4.0, -2.0, 0.0, 2.0, 4.0, 6.0};

    std::cout << std::fixed << std::setprecision(5);
    for (const double snr : snr_values) {
        const double ber = sim.run_point(snr);
        std::cout << "Eb/N0: " << std::setw(5) << std::setprecision(1) << snr << " дБ | "
                  << "BER: " << std::setw(8) << std::setprecision(5) << ber << "\n";
    }

    std::cout << "\nМоделювання завершено успішно.\n";
    return 0;
}
