#include "poisson_boundary_conditions_api.hpp"
#include <iostream>

int main() {
    using namespace physics::api;

    /* 1. Визначення геометрії сітки 200x200 вузлів з кроком 0.1 мм */
    GridGeometry grid{.dim = 2, .nx = 200, .ny = 200, .dx = 1e-4, .dy = 1e-4};

    /* 2. Налаштування розв'язувача SOR з точністю 1e-7 */
    SolverSettings settings{
        .algorithm = SolverAlgorithm::SOR,
        .tolerance = 1e-7,
        .max_iterations = 5000,
        .omega_override = 0.0 /* Автоматичний обчислення omega */
    };

    try {
        BoundaryValueProblemSolver solver(grid, settings);

        /* 3. Фіксація зовнішніх границь як заземлених (Dirichlet 0 V) */
        for (std::size_t i = 0; i < grid.nx; ++i) {
            solver.set_node_boundary(i, 0, BoundaryDescriptor{.type = BoundaryType::Dirichlet, .v_value = 0.0});
            solver.set_node_boundary(i, grid.ny - 1, BoundaryDescriptor{.type = BoundaryType::Dirichlet, .v_value = 0.0});
        }

        /* 4. Створення шини живлення +5V в центрі */
        for (std::size_t i = 80; i <= 120; ++i) {
            solver.set_node_boundary(i, 100, BoundaryDescriptor{.type = BoundaryType::Dirichlet, .v_value = 5.0});
        }

        /* 5. Запуск чисельного розв'язку */
        auto result = solver.execute();

        if (result.has_value()) {
            std::cout << "Розв'язок знайдено за " << result->iterations_spent << " ітерацій.\n";
            std::cout << "Залишкова похибка: " << result->final_residual << "\n";
            std::cout << "Електростатична енергія: " << result->total_energy_joules << " Дж\n";
        } else {
            std::cerr << "Помилка обчислень з кодом: " << static_cast<std::uint32_t>(result.error()) << "\n";
        }

    } catch (const std::exception& e) {
        std::cerr << "Виняткова ситуація: " << e.what() << "\n";
    }

    return 0;
}
