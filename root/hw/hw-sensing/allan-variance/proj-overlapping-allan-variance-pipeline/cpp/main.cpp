#include <iostream>
#include <vector>
#include <random>
#include <iomanip>
#include "allan_pipeline.hpp"

int main() {
    std::cout << "=== Паралельний конвеєр C++17 AllanVariancePipeline (std::execution::par) ===\n\n";

    constexpr std::size_t N = 100000;      // 100k точок
    constexpr double dt = 0.01;            // 100 Hz

    std::cout << "Генерація синтетичного шуму МЕМС-сенсора (N = " << N << ", dt = " << dt << " c)...\n";
    std::vector<double> sensor_stream(N);

    std::mt19937_64 rng(42);
    std::normal_distribution<double> white_noise(0.0, 0.08);       // Білий шум швидкості (ARW)
    std::normal_distribution<double> drift_noise(0.0, 0.00015);    // Випадкове блукання (RRW)

    double current_bias = 2.5; // Постійний зсув нуля +2.5 °/s
    for (std::size_t i = 0; i < N; ++i) {
        current_bias += drift_noise(rng);
        sensor_stream[i] = current_bias + white_noise(rng);
    }

    try {
        AllanVariancePipeline<double> pipeline(dt);
        pipeline.set_data(sensor_stream);

        // Формування логарифмічної сітки кроків m
        std::vector<std::size_t> m_grid = {
            1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192
        };

        std::cout << "Паралельне обчислення OADEV / MDEV на всіх доступних ядрах ЦП...\n\n";
        const auto results = pipeline.compute_parallel(m_grid);

        std::cout << std::left 
                  << std::setw(10) << "tau, c" << " | "
                  << std::setw(8)  << "m"      << " | "
                  << std::setw(14) << "OADEV (°/s)" << " | "
                  << std::setw(14) << "MDEV (°/s)"  << " | "
                  << std::setw(8)  << "EDF"    << " | "
                  << "95% Довірчий інтервал\n";
        std::cout << std::string(88, '-') << "\n";

        for (const auto& r : results) {
            if (r.adev > 0.0) {
                std::cout << std::fixed
                          << std::setw(10) << std::setprecision(3) << r.tau << " | "
                          << std::setw(8)  << r.m << " | "
                          << std::setw(14) << std::setprecision(6) << r.adev << " | "
                          << std::setw(14) << std::setprecision(6) << r.mdev << " | "
                          << std::setw(8)  << std::setprecision(1) << r.edf << " | ["
                          << std::setprecision(6) << r.adev_lower << " ... " << r.adev_upper << "]\n";
            }
        }
        std::cout << std::string(88, '-') << "\n";
        std::cout << "Розрахунок успішно завершено.\n";

    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка конвеєра: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
