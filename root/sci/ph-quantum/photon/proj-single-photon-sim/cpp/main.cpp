#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <memory>
#include <iomanip>

enum class SourceType {
    SinglePhoton,
    Coherent,
    Thermal
};

class SinglePhotonSimulator {
public:
    SinglePhotonSimulator(size_t total_bins, double dt_ns, size_t max_lag)
        : total_bins_(total_bins), dt_ns_(dt_ns), max_lag_(max_lag),
          counts_a_(total_bins, 0), counts_b_(total_bins, 0), g2_(max_lag + 1, 0.0),
          rng_(std::random_device{}()) {}

    void simulate(SourceType type, double mean_photons_per_bin) {
        std::uniform_real_distribution<double> uniform_dist(0.0, 1.0);
        std::poisson_distribution<int> poisson_dist(mean_photons_per_bin);

        for (size_t i = 0; i < total_bins_; ++i) {
            int n_photons = 0;

            switch (type) {
                case SourceType::SinglePhoton: {
                    // Квантове джерело: не більше 1 фотона за часовий біноковий інтервал
                    n_photons = (uniform_dist(rng_) < mean_photons_per_bin) ? 1 : 0;
                    break;
                }
                case SourceType::Coherent: {
                    // Класичний лазер: сувора статистика Пуассона
                    n_photons = poisson_dist(rng_);
                    break;
                }
                case SourceType::Thermal: {
                    // Теплове випромінювання: хаотичні флуктуації (розподіл Бозе — Ейнштейна)
                    double u = uniform_dist(rng_);
                    n_photons = static_cast<int>(-mean_photons_per_bin * std::log(1.0 - u + 1e-12));
                    break;
                }
            }

            // Кожен генеруваний фотон із рівною ймовірністю 50/50 потрапляє в канал A або B
            for (int p = 0; p < n_photons; ++p) {
                if (uniform_dist(rng_) < 0.5) {
                    counts_a_[i]++;
                } else {
                    counts_b_[i]++;
                }
            }
        }
    }

    void compute_g2() {
        double sum_a = 0.0;
        double sum_b = 0.0;
        for (size_t i = 0; i < total_bins_; ++i) {
            sum_a += counts_a_[i];
            sum_b += counts_b_[i];
        }

        double mean_a = sum_a / static_cast<double>(total_bins_);
        double mean_b = sum_b / static_cast<double>(total_bins_);
        double normalization = mean_a * mean_b;

        if (normalization <= 0.0) return;

        for (size_t lag = 0; lag <= max_lag_; ++lag) {
            double accum = 0.0;
            size_t pairs = total_bins_ - lag;

            for (size_t i = 0; i < pairs; ++i) {
                accum += static_cast<double>(counts_a_[i]) * counts_b_[i + lag];
            }

            g2_[lag] = (accum / static_cast<double>(pairs)) / normalization;
        }
    }

    [[nodiscard]] double get_g2(size_t lag) const { return g2_.at(lag); }

private:
    size_t total_bins_;
    double dt_ns_;
    size_t max_lag_;
    std::vector<int> counts_a_;
    std::vector<int> counts_b_;
    std::vector<double> g2_;
    std::mt19937 rng_;
};
