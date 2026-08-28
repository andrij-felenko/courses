#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <complex>
#include <numeric>
#include <iomanip>

struct SystemParams {
    double m = 1.0;
    double k = 10.0;
    double gamma = 0.5;
    double T = 300.0;
    double kB = 1.0; // Умовна стала Больцмана
    double dt = 0.001;
    size_t n_steps = 300000;
};

class LangevinSimulator {
public:
    explicit LangevinSimulator(const SystemParams& params)
        : p_(params), rng_(12345), dist_(0.0, 1.0) {}

    void run_simulation() {
        std::vector<double> x(p_.n_steps, 0.0);
        std::vector<double> v(p_.n_steps, 0.0);

        const double sigma = std::sqrt(2.0 * p_.gamma * p_.kB * p_.T / p_.dt);

        for (size_t i = 1; i < p_.n_steps; ++i) {
            double xi = dist_(rng_) * sigma;
            double a = (-p_.gamma * v[i - 1] - p_.k * x[i - 1] + xi) / p_.m;
            v[i] = v[i - 1] + a * p_.dt;
            x[i] = x[i - 1] + v[i] * p_.dt;
        }

        // Обчислення середньої кінетичної енергії у рівноважному стані
        size_t start_idx = p_.n_steps / 10;
        double sum_v2 = 0.0;
        for (size_t i = start_idx; i < p_.n_steps; ++i) {
            sum_v2 += v[i] * v[i];
        }
        double mean_v2 = sum_v2 / static_cast<double>(p_.n_steps - start_idx);
        double e_kin = 0.5 * p_.m * mean_v2;
        double expected_e_kin = 0.5 * p_.kB * p_.T;

        std::cout << std::fixed << std::setprecision(4);
        std::cout << "=== Результати чисельного експерименту Ланжевена (C++) ===\n";
        std::cout << "Очікувана середня E_kin: " << expected_e_kin << "\n";
        std::cout << "Отримана середня E_kin:  " << e_kin << "\n";
        std::cout << "Відносна помилка:       " 
                  << (std::abs(e_kin - expected_e_kin) / expected_e_kin * 100.0) << "%\n";
    }

private:
    SystemParams p_;
    std::mt19937 rng_;
    std::normal_distribution<double> dist_;
};

int main() {
    SystemParams params;
    LangevinSimulator simulator(params);
    simulator.run_simulation();
    return 0;
}
