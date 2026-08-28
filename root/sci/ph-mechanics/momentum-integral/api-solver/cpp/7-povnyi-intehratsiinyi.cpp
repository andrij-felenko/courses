#include "momentum_solver.hpp"
#include <iostream>
#include <vector>
#include <iomanip>

int main() {
    using namespace momentum;

    // 1. Задання фізичних властивостей середовища (повітря за нормальних умов)
    FluidProperties air{
        .density = 1.225,              // кг/м³
        .kinematic_viscosity = 1.5e-5  // м²/с
    };

    // 2. Налаштування конфігурації розв'язувача
    SolverConfig config{
        .mode = SolverMode::ThwaitesLaminar,
        .stop_on_separation = true
    };

    BoundaryLayerSolver solver(air, config);

    // 3. Формування дискретної сітки уздовж пластини довжиною L = 1.5 м
    constexpr std::size_t num_points = 150;
    constexpr double length = 1.5;
    constexpr double U_free = 15.0; // м/с

    std::vector<PointInput> grid;
    grid.reserve(num_points);

    for (std::size_t i = 0; i < num_points; ++i) {
        double x_val = 0.001 + (length - 0.001) * static_cast<double>(i) / (num_points - 1);
        grid.push_back(PointInput{
            .x = x_val,
            .U_e = U_free,
            .dUe_dx = 0.0 // для плоскої пластини градієнт дорівнює нулю
        });
    }

    // 4. Виконання чисельного розрахунку
    auto solution = solver.solve(grid);

    if (!solution) {
        std::cerr << "Помилка при виконанні розрахунку: " 
                  << to_string(solution.error()) << "\n";
        return 1;
    }

    // 5. Виведення підсумкових результатів
    const auto& results = solution->points;
    std::cout << std::fixed << std::setprecision(6);
    std::cout << "Успішно оброблено точок: " << results.size() << "\n";
    std::cout << "Точка x = " << results.back().x << " м:\n";
    std::cout << "  Товщина втрати імпульсу (theta): " << results.back().theta * 1000.0 << " мм\n";
    std::cout << "  Товщина зміщення (delta_star):   " << results.back().delta_star * 1000.0 << " мм\n";
    std::cout << "  Коефіцієнт формы H:               " << results.back().H << "\n";
    std::cout << "  Місцевий коефіцієнт тертя C_f:    " << results.back().C_f << "\n";
    std::cout << "  Повний опір тертя пластини:       " << solution->total_friction_drag << " Н/м\n";

    return 0;
}
