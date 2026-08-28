// Повний приклад використання C++17 API
#include <iostream>
#include <iomanip>
#include "syk_solver.hpp"

int main() {
    try {
        syk::SYKSolverConfig cfg;
        cfg.beta = 20.0;
        cfg.grid_points = 512;
        cfg.mix_alpha = 0.15;
        cfg.tolerance = 1e-7;

        std::cout << "Запуск ітераційного солуера SYK на C++17 API...\n";
        syk::SYKSolver solver(cfg);
        
        std::size_t iters = solver.solve();
        std::cout << "Солуер успішно збігся за " << iters << " ітерацій!\n";

        const auto& g_tau = solver.g_tau();
        std::cout << std::fixed << std::setprecision(8);
        std::cout << "Значення G(tau = beta/2) = " << g_tau[cfg.grid_points / 2] << "\n";
        std::cout << "Залишкова ентропія S0/N = " << solver.compute_residual_entropy() << "\n";

    } catch (const syk::SolverException& e) {
        std::cerr << "Помилка виконання солуера: " << e.what() 
                  << " (Код помилки: " << static_cast<int>(e.code()) << ")\n";
        return 1;
    } catch (const std::exception& e) {
        std::cerr << "Стандартний виняток: " << e.what() << "\n";
        return 1;
    }

    return 0;
}
