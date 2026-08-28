#include <iostream>
#include <iomanip>
#include <vector>

// Припускаємо наявність заголовочного файла C++ API
#include "circle_map.hpp"

int main() {
    using namespace physics::nonlinear::api;

    const CircleMapConfig config{
        .omega = 0.5,
        .k = 0.7,
        .transient_steps = 10000,
        .measure_steps = 50000,
        .initial_x = 0.2
    };

    const CircleMapSolver solver{config};
    const auto outcome = solver.solve(16, 1e-4);

    if (!outcome) {
        std::cerr << "Помилка обчислення C++ API!\n";
        return 1;
    }

    const auto& res = outcome.value();
    std::cout << std::fixed << std::setprecision(6);
    std::cout << "=== Результати обчислення через C++20 API ===\n";
    std::cout << "Число обертання W: " << res.rotation_number << "\n";
    std::cout << "Показник Ляпунова lambda: " << res.lyapunov_exponent << "\n";

    if (res.resonance) {
        std::cout << "Статус: Захоплення фази на резонансі "
                  << res.resonance->numerator << "/" << res.resonance->denominator
                  << " (абсолютна похибка: " << res.resonance->error << ")\n";
    } else {
        std::cout << "Статус: Квазіперіодичний режим\n";
    }

    const auto bounds_outcome = TongueBoundaryFinder::find_boundaries(0.7, 1, 2, 1e-6);
    if (bounds_outcome) {
        const auto& b = bounds_outcome.value();
        std::cout << "Межі язика 1/2 при K=0.7: Omega in ["
                  << b.omega_left << ", " << b.omega_right
                  << "], ширина = " << b.width << "\n";
    }

    return 0;
}
