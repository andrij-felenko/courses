// Моделювання дробового шуму та фактора Фано на мові C++20
#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <numeric>
#include <numbers>
#include <format>

constexpr double ELECTRON_CHARGE = 1.602176634e-19;

struct NoiseResult {
    double target_fano;
    double mean_current;
    double psd_measured;
    double psd_theoretical;
    double measured_fano;
};

class ShotNoiseSimulator {
public:
    ShotNoiseSimulator(double rate_hz, double dt_sec, std::size_t samples)
        : rate_(rate_hz), dt_(dt_sec), samples_(samples), rng_(std::random_device{}()) {}

    NoiseResult run(double fano) {
        std::vector<double> current(samples_, 0.0);
        double t = 0.0;
        const double t_max = dt_ * samples_;
        std::size_t total_events = 0;

        std::exponential_distribution<double> exp_dist(rate_);
        std::uniform_real_distribution<double> unif_dist(0.0, 1.0);

        while (t < t_max) {
            double interval = 0.0;
            if (std::abs(fano - 1.0) < 0.01) {
                // Пуассонівський процес
                interval = exp_dist(rng_);
            } else if (fano < 1.0) {
                // Субпуассонівський потік (сума k однакових інтервалів)
                int k = std::max(1, static_cast<int>(std::round(1.0 / fano)));
                double sum_val = 0.0;
                for (int i = 0; i < k; ++i) {
                    sum_val += exp_dist(rng_);
                }
                interval = (sum_val / k);
            } else {
                // Суперпуассонівський потік (згустки частинок)
                double factor = (unif_dist(rng_) < 0.2) ? (1.0 / (fano * 1.5)) : 1.0;
                interval = exp_dist(rng_) / factor;
            }

            t += interval;
            if (t < t_max) {
                auto idx = static_cast<std::size_t>(t / dt_);
                if (idx < samples_) {
                    current[idx] += ELECTRON_CHARGE / dt_;
                    total_events++;
                }
            }
        }

        // Обчислення математичного сподівання та дисперсії через стандартний алгоритм
        const double mean_current = std::accumulate(current.begin(), current.end(), 0.0) / samples_;

        double sq_sum = 0.0;
        for (double val : current) {
            double diff = val - mean_current;
            sq_sum += diff * diff;
        }
        const double variance = sq_sum / samples_;

        const double psd_measured = 2.0 * variance * dt_;
        const double psd_theoretical = 2.0 * ELECTRON_CHARGE * mean_current * fano;
        const double measured_fano = psd_measured / (2.0 * ELECTRON_CHARGE * mean_current);

        return NoiseResult{
            .target_fano = fano,
            .mean_current = mean_current,
            .psd_measured = psd_measured,
            .psd_theoretical = psd_theoretical,
            .measured_fano = measured_fano
        };
    }

private:
    double rate_;
    double dt_;
    std::size_t samples_;
    std::mt19937_64 rng_;
};

int main() {
    constexpr double rate = 1e9;
    constexpr double dt = 1e-11;
    constexpr std::size_t samples = 100000;

    ShotNoiseSimulator sim(rate, dt, samples);

    std::cout << "=== МОДЕЛЮВАННЯ ДРОБОВОГО ШУМУ ТА ФАКТОРА ФАНО (C++) ===\n\n";

    const std::vector<double> fano_list = {0.5, 1.0, 2.0};
    for (double fano : fano_list) {
        auto res = sim.run(fano);
        std::cout << std::format("Заданий фактор Фано F: {:.2f}\n", res.target_fano);
        std::cout << std::format("  Середній струм ⟨I⟩:      {:.4e} А\n", res.mean_current);
        std::cout << std::format("  Виміряна PSD S_I:        {:.4e} А²/Гц\n", res.psd_measured);
        std::cout << std::format("  Теоретична PSD (2qIF):   {:.4e} А²/Гц\n", res.psd_theoretical);
        std::cout << std::format("  Отриманий фактор Фано:   {:.3f}\n\n", res.measured_fano);
    }

    return 0;
}
