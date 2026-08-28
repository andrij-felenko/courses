module matrix:ops;

import :types; // Імпорт інтерфейсного розділу всередині того самого модуля

namespace math::internal {

[[nodiscard]] constexpr double determinant(const Matrix2x2& m) noexcept {
    return m.at(0, 0) * m.at(1, 1) - m.at(0, 1) * m.at(1, 0);
}

[[nodiscard]] constexpr Vector2 transform(const Matrix2x2& m, const Vector2& v) noexcept {
    return Vector2{
        m.at(0, 0) * v.x + m.at(0, 1) * v.y,
        m.at(1, 0) * v.x + m.at(1, 1) * v.y
    };
}

} // namespace math::internal
