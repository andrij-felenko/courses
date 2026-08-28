#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <iomanip>
#include <numeric>

// Клас ідіоматичної С++ моделі теплового шуму
class ThermalNoiseSimulator {
public:
    ThermalNoiseSimulator(double resistance, double temperature, double capacitance, double sample_rate)
        : R_(resistance), T_(temperature), C_(capacitance), fs_(sample_rate),
          gen_(std::random_device{}()) {}

    struct SimulationResult {
        double theoretical_variance;
        double empirical_variance;
        double relative_error_percent;
    };

    SimulationResult run(std::size_t num_samples) {
        constexpr double kB = 1.380649e-23;
        const double dt = 1.0 / fs_;
        const double sigma_v = std::sqrt(2.0 * kB * T_ * R_ * fs_);
        const double alpha = std::exp(-dt / (R_ * C_));

        std::normal_distribution<double> dist(0.0, sigma_v);

        double u_out = 0.0;
        double sum_sq = 0.0;

        for (std::size_t i = 0; i < num_samples; ++i) {
            const double u_in = dist(gen_);
            u_out = alpha * u_out + (1.0 - alpha) * u_in;
            sum_sq += u_out * u_out;
        }

        const double var_emp = sum_sq / static_cast<double>(num_samples);
        const double var_theo = kB * T_ / C_;
        const double rel_err = std::abs(var_emp - var_theo) / var_theo * 100.0;

        return {var_theo, var_emp, rel_err};
    }

private:
    double R_;
    double T_;
    double C_;
    double fs_;
    std::mt19937 gen_;
};

int main() {
    ThermalNoiseSimulator sim(10000.0, 300.0, 1e-11, 1e7);
    auto res = sim.run(1000000);

    std::cout << "=== Результати моделювання теплового шуму (C++17) ===\n";
    std::cout << std::scientific << std::setprecision(6);
    std::cout << "Теоретична дисперсія <U^2>: " << res.theoretical_variance << " V^2\n";
    std::cout << "Емпірична дисперсія        : " << res.empirical_variance << " V^2\n";
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Відносна похибка           : " << res.relative_error_percent << "%\n";

    return 0;
}
