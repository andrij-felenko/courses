#include "allan_pipeline.hpp"
#include <iostream>
#include <iomanip>
#include <random>

int main() {
    constexpr size_t N = 30000;
    constexpr double dt = 0.01; // 100 Гц

    std::vector<double> gyro_data(N);
    std::mt19937_64 rng(42);
    std::normal_distribution<double> white_noise(0.0, 0.015);
    std::normal_distribution<double> bias_walk(0.0, 0.00008);

    double current_bias = 0.002;
    for (size_t i = 0; i < N; ++i) {
        current_bias += bias_walk(rng);
        gyro_data[i] = white_noise(rng) + current_bias;
    }

    try {
        sensing::AllanVariancePipeline pipeline(gyro_data, dt);

        std::vector<size_t> m_clusters;
        for (size_t m = 1; m <= N / 8; m *= 2) {
            m_clusters.push_back(m);
        }

        const auto oavar_results = pipeline.compute_oavar(m_clusters, sensing::NoiseType::WFM);

        std::cout << "========================================================================\n";
        std::cout << "     C++17 ALLAN VARIANCE PIPELINE (OAVAR & 95% CONFIDENCE BOUNDS)     \n";
        std::cout << "========================================================================\n";
        std::cout << std::setw(10) << "tau [s]"
                  << std::setw(10) << "Pairs"
                  << std::setw(16) << "ADEV [rad/s]"
                  << std::setw(16) << "95% Low"
                  << std::setw(16) << "95% High"
                  << std::setw(10) << "EDF" << "\n";
        std::cout << "------------------------------------------------------------------------\n";

        for (const auto& pt : oavar_results) {
            std::cout << std::fixed << std::setprecision(3)
                      << std::setw(10) << pt.tau
                      << std::setw(10) << pt.num_pairs
                      << std::scientific << std::setprecision(5)
                      << std::setw(16) << pt.adev
                      << std::setw(16) << pt.adev_min
                      << std::setw(16) << pt.adev_max
                      << std::fixed << std::setprecision(1)
                      << std::setw(10) << pt.edf << "\n";
        }
        std::cout << "========================================================================\n";

    } catch (const std::exception& ex) {
        std::cerr << "Помилка конвеєра: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
