#include <iostream>

int main() {
    using namespace thermal;

    try {
        SolverConfig cfg{
            .grid_x = 50,
            .grid_y = 50,
            .dx = 0.002,
            .dy = 0.002,
            .dt = 0.001,
            .max_time = 5.0,
            .tolerance = 1e-5,
            .is_transient = true
        };

        MaterialProperties mat{
            .conductivity = 167.0,
            .density = 2700.0,
            .specific_heat = 896.0,
            .emissivity = 0.85
        };

        ThermalSolver solver(cfg, mat);

        std::array<BoundaryCondition, 4> bcs{
            BoundaryCondition{BoundaryType::Dirichlet, 100.0},
            BoundaryCondition{BoundaryType::Dirichlet, 20.0},
            BoundaryCondition{BoundaryType::Robin, 0.0, 25.0, 20.0},
            BoundaryCondition{BoundaryType::Robin, 0.0, 25.0, 20.0}
        };

        solver.set_boundary_conditions(bcs);

        auto result = solver.run();
        if (result.has_value()) {
            const auto grid = solver.temperature_grid();
            const auto center_idx = (cfg.grid_y / 2) * cfg.grid_x + (cfg.grid_x / 2);
            std::cout << "Розрахунок завершено. Т_центр = " << grid[center_idx] << " °C\n";
        } else {
            std::cerr << "Помилка розв'язувача, код: " << static_cast<int>(result.error()) << '\n';
        }
    } catch (const std::exception& ex) {
        std::cerr << "Виняток: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
