// Simulation of Polarization Diversity in Rayleigh Fading (C++17)
#include <iostream>
#include <vector>
#include <complex>
#include <random>
#include <cmath>
#include <iomanip>

struct SimResults {
    double rho{0.0};
    double imbalance_db{0.0};
    double outage_single{0.0};
    double outage_sc{0.0};
    double outage_mrc{0.0};
};

class DiversitySimulator {
public:
    DiversitySimulator(double mean_snr_db, double threshold_db)
        : snr_linear_(std::pow(10.0, mean_snr_db / 10.0)),
          thresh_linear_(std::pow(10.0, threshold_db / 10.0)),
          rng_(12345), /* Fixed seed for reproducibility */
          norm_dist_(0.0, 1.0 / std::sqrt(2.0)) {}

    SimResults run(std::size_t samples, double rho, double imbalance_db = 0.0) {
        const double rho_c = std::sqrt(rho);
        const double factor_ortho = std::sqrt(1.0 - rho_c * rho_c);
        const double imbalance_factor = std::sqrt(std::pow(10.0, -imbalance_db / 10.0));

        std::size_t single_out = 0;
        std::size_t sc_out = 0;
        std::size_t mrc_out = 0;

        for (std::size_t i = 0; i < samples; ++i) {
            std::complex<double> w1{norm_dist_(rng_), norm_dist_(rng_)};
            std::complex<double> w2{norm_dist_(rng_), norm_dist_(rng_)};

            std::complex<double> h1 = w1;
            std::complex<double> h2 = (rho_c * w1 + factor_ortho * w2) * imbalance_factor;

            double g1 = std::norm(h1) * snr_linear_;
            double g2 = std::norm(h2) * snr_linear_;

            double g_sc = std::max(g1, g2);
            double g_mrc = g1 + g2;

            if (g1 < thresh_linear_) ++single_out;
            if (g_sc < thresh_linear_) ++sc_out;
            if (g_mrc < thresh_linear_) ++mrc_out;
        }

        return {
            rho,
            imbalance_db,
            static_cast<double>(single_out) / static_cast<double>(samples),
            static_cast<double>(sc_out) / static_cast<double>(samples),
            static_cast<double>(mrc_out) / static_cast<double>(samples)
        };
    }

private:
    double snr_linear_;
    double thresh_linear_;
    std::mt19937 rng_;
    std::normal_distribution<double> norm_dist_;
};

int main() {
    constexpr std::size_t num_samples = 2'000'000;
    constexpr double mean_snr_db = 15.0;
    constexpr double threshold_db = 0.0;

    std::cout << "=== Polarization Diversity Channel Simulation (C++17) ===\n";
    std::cout << "Samples: " << num_samples << ", Mean SNR: " << mean_snr_db 
              << " dB, Threshold: " << threshold_db << " dB\n\n";
    std::cout << std::left << std::setw(12) << "Corr (rho)"
              << std::setw(14) << "Imbalance"
              << std::setw(18) << "Outage Single"
              << std::setw(18) << "Outage SC"
              << std::setw(18) << "Outage MRC" << "\n";
    std::cout << std::string(80, '-');
    std::cout << "\n";

    DiversitySimulator sim(mean_snr_db, threshold_db);
    const std::vector<double> rhos{0.0, 0.3, 0.5, 0.7, 0.9};

    for (double rho : rhos) {
        auto res = sim.run(num_samples, rho, 0.0);
        std::cout << std::left << std::setw(12) << std::fixed << std::setprecision(1) << res.rho
                  << std::setw(14) << std::setprecision(1) << res.imbalance_db
                  << std::setw(18) << std::setprecision(4) << res.outage_single
                  << std::setw(18) << std::setprecision(5) << res.outage_sc
                  << std::setw(18) << std::setprecision(5) << res.outage_mrc << "\n";
    }

    std::cout << "\n--- Test with Power Imbalance (Gamma = 4.0 dB) ---\n";
    for (double rho : rhos) {
        auto res = sim.run(num_samples, rho, 4.0);
        std::cout << std::left << std::setw(12) << std::fixed << std::setprecision(1) << res.rho
                  << std::setw(14) << std::setprecision(1) << res.imbalance_db
                  << std::setw(18) << std::setprecision(4) << res.outage_single
                  << std::setw(18) << std::setprecision(5) << res.outage_sc
                  << std::setw(18) << std::setprecision(5) << res.outage_mrc << "\n";
    }

    return 0;
}
