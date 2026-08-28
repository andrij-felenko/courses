// =========================================================================
// Повний приклад на мові C++20 (Аналіз стробоскопічного відображення)
// =========================================================================
#include <iostream>
#include <cmath>
#include "poincare_sec.hpp"

int main() {
    using State2D = std::array<double, 2>;

    // Лямбда-вираз для векторного поля осцилятора
    auto duffing = [](const State2D& s, double t, State2D& out) {
        out[0] = s[1];
        out[1] = -0.2 * s[1] + s[0] - s[0] * s[0] * s[0] + 0.3 * std::cos(t);
    };

    // Секуща поверхня v = 0
    auto section_plane = [](const State2D& s, State2D& grad) {
        grad[0] = 0.0;
        grad[1] = 1.0;
        return s[1];
    };

    poincare::SolverConfig cfg{
        .rel_tol = 1e-10,
        .abs_tol = 1e-12,
        .initial_dt = 0.01
    };

    poincare::MapSolver<2, decltype(duffing), decltype(section_plane)> solver(duffing, section_plane, cfg);

    State2D initial_state{0.1, 0.0};
    auto series_result = solver.compute_series(initial_state, 5);

    if (!series_result) {
        std::cerr << "Помилка розрахунку перерізу Пуанкаре у C++!\n";
        return 1;
    }

    for (std::size_t i = 0; const auto& pt : *series_result) {
        std::cout << "Точка " << i++ << ": t = " << pt.time 
                  << ", state = [" << pt.state[0] << ", " << pt.state[1] << "]"
                  << ", кроків = " << pt.steps_executed << "\n";
    }

    return 0;
}
