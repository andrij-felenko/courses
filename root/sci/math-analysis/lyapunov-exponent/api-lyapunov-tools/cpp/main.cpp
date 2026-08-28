// main.cpp - Приклад використання LyapunovLab API мовою C++20
#include "lyapunov_lab.hpp"
#include <iostream>
#include <iomanip>
#include <array>

int main() {
    using namespace lyapunov_lab;

    Config cfg{
        .dim = 3,
        .dt = 0.01,
        .total_steps = 50000,
        .transient_steps = 5000,
        .qr_period = 1,
        .method = IntegratorType::RK4
    };

    System sys{
        .rhs = [](double, std::span<const double> x, std::span<double> dxdt) {
            dxdt[0] = 10.0 * (x[1] - x[0]);
            dxdt[1] = x[0] * (28.0 - x[2]) - x[1];
            dxdt[2] = x[0] * x[1] - (8.0 / 3.0) * x[2];
        },
        .jacobian = [](double, std::span<const double> x, std::span<double> J) {
            J[0] = -10.0; J[1] = 10.0;  J[2] = 0.0;
            J[3] = 28.0 - x[2]; J[4] = -1.0; J[5] = -x[0];
            J[6] = x[1];  J[7] = x[0];  J[8] = -8.0 / 3.0;
        }
    };

    std::array<double, 3> init_state{1.0, 1.0, 1.0};
    Analyzer analyzer{cfg};

    auto result = analyzer.compute(sys, init_state);
    if (result.has_value()) {
        const auto& metrics = result.value();
        std::cout << std::fixed << std::setprecision(4);
        std::cout << "Обчислення завершено успішно (C++20):\n";
        std::cout << "  lambda_1 = " << metrics.spectrum[0] << "\n";
        std::cout << "  lambda_2 = " << metrics.spectrum[1] << "\n";
        std::cout << "  lambda_3 = " << metrics.spectrum[2] << "\n";
        std::cout << "  D_L = " << metrics.lyapunov_dimension << "\n";
    } else {
        std::cerr << "Помилка: " << to_string(result.error()) << "\n";
    }

    return 0;
}
