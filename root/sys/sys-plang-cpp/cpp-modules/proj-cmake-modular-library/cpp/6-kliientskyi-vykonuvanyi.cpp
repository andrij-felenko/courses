import matrix;
import <iostream>;

int main() {
    math::Matrix2x2 a;
    a.at(0, 0) = 2.0; a.at(0, 1) = 1.0;
    a.at(1, 0) = 1.0; a.at(1, 1) = 3.0;

    math::Vector2 b{5.0, 5.0};

    math::print_matrix(a, "Матриця A");

    const auto sol = math::solve_2x2(a, b);
    if (sol.has_value()) {
        std::cout << "Розв'язок Ax = b: x = " << sol->x << ", y = " << sol->y << "\n";
    } else {
        std::cout << "Система не має розв'язку\n";
    }

    auto err = math::save_to_binary_file("matrix.bin", a);
    if (err) {
        std::cout << "Помилка запису файлу: " << err.message() << "\n";
    } else {
        std::cout << "Матрицю успішно записано у matrix.bin\n";
    }

    return 0;
}
