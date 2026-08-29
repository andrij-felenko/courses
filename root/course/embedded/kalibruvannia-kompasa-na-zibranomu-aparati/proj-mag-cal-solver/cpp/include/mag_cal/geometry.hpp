// ===========================================================================
//  mag_cal/geometry.hpp — вектор і симетрична матриця 3×3.
//  Усе, що можна порахувати на етапі компіляції, позначено constexpr:
//  одинична матриця не має коштувати жодної інструкції під час старту.
// ===========================================================================
#pragma once

#include <array>
#include <cmath>

namespace mag_cal {

struct Vec3 {
    float x{0.0F};
    float y{0.0F};
    float z{0.0F};

    [[nodiscard]] constexpr Vec3 operator+(const Vec3& rhs) const noexcept {
        return {x + rhs.x, y + rhs.y, z + rhs.z};
    }
    [[nodiscard]] constexpr Vec3 operator-(const Vec3& rhs) const noexcept {
        return {x - rhs.x, y - rhs.y, z - rhs.z};
    }
    [[nodiscard]] constexpr Vec3 operator*(float k) const noexcept {
        return {x * k, y * k, z * k};
    }
    [[nodiscard]] constexpr float dot(const Vec3& rhs) const noexcept {
        return x * rhs.x + y * rhs.y + z * rhs.z;
    }
    [[nodiscard]] float norm() const noexcept { return std::sqrt(dot(*this)); }

    // Нульовий або зіпсований вектор дає надір: напрямок «угору» завжди
    // безпечніший за NaN, що поповзе далі в оцінювач положення.
    [[nodiscard]] Vec3 normalized() const noexcept {
        const float n = norm();
        if (!(n > 1e-6F)) {
            return {0.0F, 0.0F, 1.0F};
        }
        return *this * (1.0F / n);
    }
};

class Mat3 {
public:
    using Rows = std::array<std::array<float, 3>, 3>;

    constexpr Mat3() = default;
    constexpr explicit Mat3(const Rows& rows) noexcept : rows_{rows} {}

    // Симетрична матриця з шести незалежних параметрів підгонки
    [[nodiscard]] static constexpr Mat3 symmetric(float m11, float m12, float m13,
                                                  float m22, float m23,
                                                  float m33) noexcept {
        return Mat3{Rows{{{m11, m12, m13}, {m12, m22, m23}, {m13, m23, m33}}}};
    }

    [[nodiscard]] constexpr float at(std::size_t i, std::size_t j) const noexcept {
        return rows_[i][j];
    }

    [[nodiscard]] constexpr Vec3 operator*(const Vec3& v) const noexcept {
        return {rows_[0][0] * v.x + rows_[0][1] * v.y + rows_[0][2] * v.z,
                rows_[1][0] * v.x + rows_[1][1] * v.y + rows_[1][2] * v.z,
                rows_[2][0] * v.x + rows_[2][1] * v.y + rows_[2][2] * v.z};
    }

    [[nodiscard]] constexpr float determinant() const noexcept {
        return rows_[0][0] * (rows_[1][1] * rows_[2][2] - rows_[1][2] * rows_[2][1]) -
               rows_[0][1] * (rows_[1][0] * rows_[2][2] - rows_[1][2] * rows_[2][0]) +
               rows_[0][2] * (rows_[1][0] * rows_[2][1] - rows_[1][1] * rows_[2][0]);
    }

    // Власні числа симетричної матриці, спаданням (замкнена формула Сміта)
    [[nodiscard]] std::array<float, 3> symmetric_eigenvalues() const noexcept;

    // |λmax| / |λmin|; вироджена матриця дає велике скінченне число
    [[nodiscard]] float condition_number() const noexcept;

    [[nodiscard]] bool all_finite() const noexcept;

private:
    Rows rows_{{{1.0F, 0.0F, 0.0F}, {0.0F, 1.0F, 0.0F}, {0.0F, 0.0F, 1.0F}}};
};

}  // namespace mag_cal
