#include <iostream>
#include <vector>
#include <span>
#include "matrix_perm.hpp"

int main() {
    const std::vector<double> matrix = {
        1.0, 2.0, 0.0,
        3.0, 1.0, 4.0,
        0.0, 2.0, 1.0
    };
    const std::size_t n = 3;

    math::matrix::permanent_solver solver{
        {.alg = math::matrix::algorithm::glynn}
    };

    auto result = solver.compute(matrix, n);

    if (result.has_value()) {
        std::cout << "Перманент матриці 3x3 дорівнює: " << result.value() << '\n';
    } else {
        std::cerr << "Помилка обчислення перманента\n";
        return 1;
    }

    return 0;
}
