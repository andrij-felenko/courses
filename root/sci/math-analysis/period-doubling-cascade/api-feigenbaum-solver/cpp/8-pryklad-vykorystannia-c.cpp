#include <feigenbaum.hpp>
#include <iostream>

int main() {
    feigenbaum::Config config{
        .r_min = 3.0,
        .r_max = 3.57,
        .r_steps = 2000,
        .transient_iters = 2000,
        .orbit_iters = 1000
    };

    feigenbaum::Solver solver(config);
    
    // Знаходження надстійкої точки R_3 (період 8)
    auto result = solver.find_superstable(3, 3.5546);
    
    if (result) {
        std::cout << "Знайдено R_3: " << result->r_superstable << "\n";
        std::cout << "Показник Ляпунова: " << result->lyapunov << "\n";
    } else {
        std::cerr << "Помилка розрахунку: " << static_cast<int>(result.error()) << "\n";
    }

    return 0;
}
