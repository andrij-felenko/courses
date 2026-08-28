#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <iomanip>
#include <numeric>
#include <algorithm>

struct ChannelStats {
    double mean_amplitude{0.0};
    double mean_power{0.0};
    double outage_probability{0.0};
    double amount_of_fading{0.0};
};

class FadingChannelSimulator {
private:
    std::mt19937 rng_;
    std::normal_distribution<double> norm_dist_{0.0, 1.0};

public:
    explicit FadingChannelSimulator(uint32_t seed = 42) : rng_(seed) {}

    [[nodiscard]] double sampleRayleigh(double sigma) {
        double i = sigma * norm_dist_(rng_);
        double q = sigma * norm_dist_(rng_);
        return std::hypot(i, q);
    }

    [[nodiscard]] double sampleRician(double K_lin, double sigma) {
        double s = std::sqrt(2.0 * K_lin * sigma * sigma);
        double i = s + sigma * norm_dist_(rng_);
        double q = sigma * norm_dist_(rng_);
        return std::hypot(i, q);
    }

    [[nodiscard]] double sampleNakagami(double m, double omega) {
        if (std::abs(m - 1.0) < 1e-3) {
            return sampleRayleigh(std::sqrt(omega / 2.0));
        }

        int k_count = static_cast<int>(2.0 * m + 0.5);
        if (k_count < 1) k_count = 1;

        double sum_sq = 0.0;
        double scale = std::sqrt(omega / (2.0 * m));
        for (int k = 0; k < k_count; ++k) {
            double val = scale * norm_dist_(rng_);
            sum_sq += val * val;
        }
        return std::sqrt(sum_sq);
    }

    [[nodiscard]] static ChannelStats analyze(const std::vector<double>& samples, double threshold) {
        ChannelStats stats;
        const double n = static_cast<double>(samples.size());
        
        double sum_r = 0.0;
        double sum_p = 0.0;
        double sum_p2 = 0.0;
        size_t outages = 0;

        for (double r : samples) {
            double p = r * r;
            sum_r += r;
            sum_p += p;
            sum_p2 += p * p;
            if (r < threshold) {
                ++outages;
            }
        }

        stats.mean_amplitude = sum_r / n;
        stats.mean_power = sum_p / n;
        stats.outage_probability = static_cast<double>(outages) / n;

        double var_p = (sum_p2 / n) - (stats.mean_power * stats.mean_power);
        stats.amount_of_fading = var_p / (stats.mean_power * stats.mean_power);

        return stats;
    }
};

int main() {
    FadingChannelSimulator sim(12345);
    constexpr size_t N = 100000;
    constexpr double threshold = 0.3;

    std::vector<double> rayleigh_samples(N);
    std::vector<double> rician_samples(N);
    std::vector<double> nakagami_samples(N);

    for (size_t i = 0; i < N; ++i) {
        rayleigh_samples[i] = sim.sampleRayleigh(0.7071);
        rician_samples[i]   = sim.sampleRician(3.98, 0.316);
        nakagami_samples[i] = sim.sampleNakagami(0.5, 1.0);
    }

    auto st_ray = FadingChannelSimulator::analyze(rayleigh_samples, threshold);
    auto st_ric = FadingChannelSimulator::analyze(rician_samples, threshold);
    auto st_nak = FadingChannelSimulator::analyze(nakagami_samples, threshold);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=== Обчислення характеристик радіоканалу (C++) ===\n\n";
    std::cout << "Поріг амплітуди R_th = " << threshold << "\n\n";
    
    std::cout << "1. Канал Релея (NLOS):\n"
              << "   - Середня амплітуда: " << st_ray.mean_amplitude << "\n"
              << "   - Середня потужність:  " << st_ray.mean_power << "\n"
              << "   - Outage Probability: " << st_ray.outage_probability * 100.0 << " %\n"
              << "   - Amount of Fading:   " << st_ray.amount_of_fading << " (теоретично 1.0000)\n\n";

    std::cout << "2. Канал Райса (K = 6 дБ):\n"
              << "   - Середня амплітуда: " << st_ric.mean_amplitude << "\n"
              << "   - Середня потужність:  " << st_ric.mean_power << "\n"
              << "   - Outage Probability: " << st_ric.outage_probability * 100.0 << " %\n"
              << "   - Amount of Fading:   " << st_ric.amount_of_fading << "\n\n";

    std::cout << "3. Канал Накагамі (m = 0.5, severe):\n"
              << "   - Середня амплітуда: " << st_nak.mean_amplitude << "\n"
              << "   - Середня потужність:  " << st_nak.mean_power << "\n"
              << "   - Outage Probability: " << st_nak.outage_probability * 100.0 << " %\n"
              << "   - Amount of Fading:   " << st_nak.amount_of_fading << " (теоретично 2.0000)\n";

    return 0;
}
