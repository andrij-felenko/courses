#include "FloquetSolver.hpp"
#include <iostream>
#include <cmath>

int main() {
    using namespace Physics::Mechanics;

    FloquetConfig config{
        .dim = 2,
        .period = 3.14159265358979323846,
        .steps = 1000,
        .tolerance = 1e-5
    };

    FloquetSolver solver(config);

    double a = 1.5;
    double q = 0.2;

    auto sys_fn = [a, q](double t, std::span<double> out_matrix) {
        double f_t = a - 2.0 * q * std::cos(2.0 * t);
        out_matrix[0] = 0.0;
        out_matrix[1] = 1.0;
        out_matrix[2] = -f_t;
        out_matrix[3] = 0.0;
    };

    auto result = solver.solve(sys_fn);

    if (result) {
        std::cout << "Обчислення C++ успішне!\n";
        std::cout << "Слід M: " << result->trace << "\n";
        std::cout << "Максимальний модуль |lambda|: " << result->max_modulus << "\n";
        std::cout << "Система стійка: " << (result->is_stable ? "ТАК" : "НІ");
    } else {
        std::cerr << "Помилка обчислення з кодом: " << static_cast<int>(result.error()) << "\n";
    }

    return 0;
}
