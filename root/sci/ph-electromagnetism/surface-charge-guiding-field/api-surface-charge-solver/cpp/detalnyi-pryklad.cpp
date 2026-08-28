#include <iostream>
#include <vector>
#include <iomanip>
#include "surface_charge_solver.hpp"

int main() {
    using namespace ElectroDynamics;

    // 1. Створення конфігурації обчислювальної сітки 128x128 з кроком 0.5 мм
    SolverConfig config;
    config.grid_nx = 128;
    config.grid_ny = 128;
    config.mesh_step_m = 0.0005; // Крок 0.5 мм
    config.relaxation_omega = 1.88;
    config.tolerance_volts = 1e-7;
    config.max_iters = 8000;
    config.engine = SolverEngine::SOR_Relaxation;
    config.enable_poynting_calc = true;

    // 2. Ініціалізація солівера
    SurfaceChargeSolver solver(config);

    // 3. Задання мідної підвідної жилу (σ = 5.8e7 См/м)
    solver.set_rectangular_conductor(10, 50, 40, 20, 5.8e7);

    // 4. Задання вуглецевого резистора (σ = 1e3 См/м) після мідного дроту
    solver.set_rectangular_conductor(50, 50, 30, 20, 1.0e3);

    // 5. Задання вихідного мідного дроту до заземлення
    solver.set_rectangular_conductor(80, 50, 40, 20, 5.8e7);

    // 6. Фіксація потенціалу джерела V_in = 12.0 В на вхідному електроді (x=10)
    for (std::size_t y = 50; y <= 70; ++y) {
        solver.set_node(10, y, BoundaryType::DirichletFix, 12.0, 5.8e7);
    }

    // 7. Фіксація потенціалу заземлення V_out = 0.0 В на вихідному електроді (x=120)
    for (std::size_t y = 50; y <= 70; ++y) {
        solver.set_node(120, y, BoundaryType::DirichletFix, 0.0, 5.8e7);
    }

    // 8. Запуск чисельного обчислення
    std::cout << "Запуск чисельного розрахунку полів та поверневих зарядів...\n";
    SolverStatus status = solver.compute();

    if (status != SolverStatus::Success) {
        std::cerr << "Розрахунок завершився з помилкою! Код статусу: " 
                  << static_cast<int>(status) << '\n';
        return 1;
    }

    // 9. Вилучення обчислених фізичних величин
    const double sigma_entry = solver.get_surface_charge(50, 60); // Стик мідь -> резистор
    const double sigma_exit  = solver.get_surface_charge(80, 60); // Стик резистор -> мідь

    std::cout << std::scientific << std::setprecision(4);
    std::cout << "Успішно обчислено!\n";
    std::cout << "Позитивний міжфазний заряд на вхідній межі резистора: " 
              << sigma_entry << " Кулон/м²\n";
    std::cout << "Негативний міжфазний заряд на вихідній межі резистора: " 
              << sigma_exit << " Кулон/м²\n";

    // 10. Розрахунок потоку вектора Пойнтінга крізь бічну поверхню резистора
    const double poynting_power = solver.get_poynting_flux_watts(50, 50, 80, 70);
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "Потік електромагнітної енергії Пойнтінга, що входить у резистор: " 
              << poynting_power << " Ватт\n";

    // 11. Експорт сітки у файл CSV для подальшого аналізу
    if (solver.export_to_csv("resistor_field_results.csv")) {
        std::cout << "Результати успішно збережено у файл resistor_field_results.csv\n";
    }

    return 0;
}
