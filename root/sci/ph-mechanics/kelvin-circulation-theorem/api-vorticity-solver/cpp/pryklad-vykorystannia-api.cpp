#include "vorticity_solver.hpp"
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>

int main() {
    try {
        fluid::SolverConfig config{
            .nx = 128,
            .ny = 128,
            .dx = 0.01,
            .dy = 0.01,
            .dt = 0.001,
            .viscosity = 0.0,
            .bc_type = fluid::BoundaryCondition::Periodic
        };

        fluid::VorticitySolver solver(config);

        std::vector<double> omega(config.nx * config.ny);
        for (std::size_t j = 0; j < config.ny; ++j) {
            for (std::size_t i = 0; i < config.nx; ++i) {
                double x = i * config.dx - 0.64;
                double y = j * config.dy - 0.64;
                omega[j * config.nx + i] = 10.0 * std::exp(-(x * x + y * y) / 0.02);
            }
        }
        solver.set_vorticity(omega);

        const std::vector<fluid::Point2D> contour{
            {0.40, 0.40},
            {0.88, 0.40},
            {0.88, 0.88},
            {0.40, 0.88}
        };

        auto stats_init = solver.compute_circulation(contour);
        std::cout << std::fixed << std::setprecision(6);
        std::cout << "Початкова циркуляція Г0 = " << stats_init.circulation << " м2/с\n";

        for (int step = 0; step < 100; ++step) {
            solver.step();
        }

        auto stats_final = solver.compute_circulation(contour);
        std::cout << "Кінцева циркуляція   Г1 = " << stats_final.circulation << " м2/с\n";
        std::cout << "Відносна зміна dГ/Г0    = " << std::scientific << std::setprecision(2)
                  << std::abs(stats_final.circulation - stats_init.circulation) / stats_init.circulation
                  << "\n";

    } catch (const std::exception& ex) {
        std::cerr << "Виняток: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
