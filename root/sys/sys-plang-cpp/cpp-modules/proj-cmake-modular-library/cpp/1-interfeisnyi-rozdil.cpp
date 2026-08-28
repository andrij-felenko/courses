export module matrix:types;

import <array>;
import <cstddef>;

export namespace math {

struct Vector2 {
    double x{0.0};
    double y{0.0};
};

struct Matrix2x2 {
    std::array<double, 4> data{1.0, 0.0, 0.0, 1.0}; // Одинична матриця за замовчуванням

    [[nodiscard]] constexpr double at(std::size_t row, std::size_t col) const noexcept {
        return data[row * 2 + col];
    }

    [[nodiscard]] constexpr double& at(std::size_t row, std::size_t col) noexcept {
        return data[row * 2 + col];
    }
};

} // namespace math
