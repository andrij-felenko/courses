export module matrix;

// Реекспорт: усі клієнти matrix автоматично бачать типи з :types та операції збереження з :storage
export import :types;
export import :storage;

// Приватний імпорт: внутрішні алгоритми потрібні тут, але не виходять назовні
import :ops;

import <optional>;
import <string>;

export namespace math {

[[nodiscard]] Matrix2x2 multiply(const Matrix2x2& a, const Matrix2x2& b) noexcept {
    Matrix2x2 res;
    for (std::size_t r = 0; r < 2; ++r) {
        for (std::size_t c = 0; c < 2; ++c) {
            res.at(r, c) = a.at(r, 0) * b.at(0, c) + a.at(r, 1) * b.at(1, c);
        }
    }
    return res;
}

[[nodiscard]] std::optional<Vector2> solve_2x2(const Matrix2x2& a, const Vector2& b) noexcept {
    const double det = internal::determinant(a);
    constexpr double eps = 1e-12;
    if (det > -eps && det < eps) {
        return std::nullopt; // Матриця вироджена
    }

    const double inv_det = 1.0 / det;
    return Vector2{
        (b.x * a.at(1, 1) - b.y * a.at(0, 1)) * inv_det,
        (a.at(0, 0) * b.y - a.at(1, 0) * b.x) * inv_det
    };
}

// Оголошення функції друку: її реалізацію навмисно винесено у matrix_io.cpp
void print_matrix(const Matrix2x2& m, const std::string& label);

} // namespace math
