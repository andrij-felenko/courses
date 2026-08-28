#include "prandtl_solver.hpp"
#include <iostream>
#include <iomanip>

int main() {
    using namespace fluid;

    // 1. Отримуємо властивості повітря при T = 300 K
    auto air_props = PrandtlSolver::getProperties(FluidType::Air, 300.0);
    if (!air_props) {
        std::cerr << "Помилка обчислення властивостей повітря!\n";
        return 1;
    }

    // 2. Розраховуємо примежовий шар на пластині x = 0.5 м, U = 20 м/с
    auto air_bl = PrandtlSolver::calcBoundaryLayer(*air_props, 20.0, 0.5);
    if (!air_bl) {
        std::cerr << "Помилка розрахунку примежового шару!\n";
        return 1;
    }

    std::cout << "=== Теплообмін у повітрі (Pr = " << air_props->prandtl_number << ") ===\n";
    std::cout << "Re_x: " << air_bl->reynolds_x << "\n";
    std::cout << "Товщина швидкісного шару δ_v: " << air_bl->delta_v * 1000.0 << " мм\n";
    std::cout << "Товщина теплового шару δ_t:    " << air_bl->delta_t * 1000.0 << " мм\n";
    std::cout << "Коефіцієнт тепловіддачі h:    " << air_bl->heat_transfer_h << " Вт/(м²·К)\n\n";

    // 3. Отримуємо властивості рідкого натрію при T = 600 K
    auto na_props = PrandtlSolver::getProperties(FluidType::LiquidSodium, 600.0);
    auto na_bl = PrandtlSolver::calcBoundaryLayer(*na_props, 5.0, 0.5);

    std::cout << "=== Теплообмін у рідкому натрії (Pr = " << na_props->prandtl_number << ") ===\n";
    std::cout << "Re_x: " << na_bl->reynolds_x << "\n";
    std::cout << "Товщина швидкісного шару δ_v: " << na_bl->delta_v * 1000.0 << " мм\n";
    std::cout << "Товщина теплового шару δ_t:    " << na_bl->delta_t * 1000.0 << " мм\n";
    std::cout << "Коефіцієнт тепловіддачі h:    " << na_bl->heat_transfer_h << " Вт/(м²·К)\n";

    return 0;
}
