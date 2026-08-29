#pragma once

// Базова алгебра просторових перетворень. C++23: далі в модулі йдуть
// std::expected та std::span, тому й тут нічого не стримуємось.
#include <algorithm>
#include <array>
#include <cmath>
#include <optional>

namespace nav {

inline constexpr float kGravity = 9.80665F;   // м/с², стандартне значення

struct Vector3 {
    float x{};
    float y{};
    float z{};

    constexpr Vector3 operator+(const Vector3& r) const noexcept { return {x + r.x, y + r.y, z + r.z}; }
    constexpr Vector3 operator-(const Vector3& r) const noexcept { return {x - r.x, y - r.y, z - r.z}; }
    constexpr Vector3 operator*(float k) const noexcept { return {x * k, y * k, z * k}; }
    constexpr Vector3 operator-() const noexcept { return {-x, -y, -z}; }

    constexpr Vector3& operator+=(const Vector3& r) noexcept {
        x += r.x; y += r.y; z += r.z;
        return *this;
    }

    [[nodiscard]] constexpr float dot(const Vector3& r) const noexcept {
        return x * r.x + y * r.y + z * r.z;
    }

    [[nodiscard]] constexpr Vector3 cross(const Vector3& r) const noexcept {
        return {y * r.z - z * r.y, z * r.x - x * r.z, x * r.y - y * r.x};
    }

    [[nodiscard]] float norm() const noexcept { return std::sqrt(dot(*this)); }

    [[nodiscard]] bool finite() const noexcept {
        return std::isfinite(x) && std::isfinite(y) && std::isfinite(z);
    }

    // Напрямку нульового вектора не існує — і тип це каже, а не коментар.
    [[nodiscard]] std::optional<Vector3> normalized() const noexcept {
        const float n = norm();
        if (!std::isfinite(n) || n < 1e-9F) return std::nullopt;
        return *this * (1.0F / n);
    }
};

class Matrix3 {
public:
    std::array<std::array<float, 3>, 3> r{};   // по рядках: r[рядок][стовпець]

    static constexpr Matrix3 identity() noexcept {
        return Matrix3{{{{1.0F, 0.0F, 0.0F}, {0.0F, 1.0F, 0.0F}, {0.0F, 0.0F, 1.0F}}}};
    }

    constexpr Vector3 operator*(const Vector3& v) const noexcept {
        return {r[0][0] * v.x + r[0][1] * v.y + r[0][2] * v.z,
                r[1][0] * v.x + r[1][1] * v.y + r[1][2] * v.z,
                r[2][0] * v.x + r[2][1] * v.y + r[2][2] * v.z};
    }

    constexpr Matrix3 operator*(const Matrix3& b) const noexcept {
        Matrix3 out{};
        for (int i = 0; i < 3; ++i) {
            for (int j = 0; j < 3; ++j) {
                out.r[i][j] = r[i][0] * b.r[0][j] + r[i][1] * b.r[1][j] + r[i][2] * b.r[2][j];
            }
        }
        return out;
    }

    [[nodiscard]] constexpr Matrix3 transposed() const noexcept {
        Matrix3 out{};
        for (int i = 0; i < 3; ++i)
            for (int j = 0; j < 3; ++j) out.r[i][j] = r[j][i];
        return out;
    }

    [[nodiscard]] constexpr float det() const noexcept {
        return r[0][0] * (r[1][1] * r[2][2] - r[1][2] * r[2][1])
             - r[0][1] * (r[1][0] * r[2][2] - r[1][2] * r[2][0])
             + r[0][2] * (r[1][0] * r[2][1] - r[1][1] * r[2][0]);
    }

    // Перенесення коваріації між базисами: P' = R · P · Rᵀ.
    [[nodiscard]] constexpr Matrix3 similarity(const Matrix3& p) const noexcept {
        return (*this) * p * transposed();
    }

    [[nodiscard]] float orthogonality_error() const noexcept {
        const Matrix3 e = transposed() * (*this);
        float worst = 0.0F;
        for (int i = 0; i < 3; ++i) {
            for (int j = 0; j < 3; ++j) {
                const float ref = (i == j) ? 1.0F : 0.0F;
                worst = std::max(worst, std::fabs(e.r[i][j] - ref));
            }
        }
        return worst;
    }

    // Грам-Шмідт по рядках: найближчий справжній поворот.
    [[nodiscard]] std::optional<Matrix3> orthonormalized() const noexcept {
        const auto row = [this](int i) { return Vector3{r[i][0], r[i][1], r[i][2]}; };
        const auto r0 = row(0).normalized();
        if (!r0) return std::nullopt;
        const Vector3 raw1 = row(1) - (*r0) * row(1).dot(*r0);
        const auto r1 = raw1.normalized();
        if (!r1) return std::nullopt;
        const Vector3 r2 = r0->cross(*r1);
        return Matrix3{{{{r0->x, r0->y, r0->z}, {r1->x, r1->y, r1->z}, {r2.x, r2.y, r2.z}}}};
    }
};

// Перехід NED <-> ENU. Матриця обернена сама до себе, тому напрямок один на обидва боки.
inline constexpr Matrix3 kNedEnu{{{{0.0F, 1.0F, 0.0F}, {1.0F, 0.0F, 0.0F}, {0.0F, 0.0F, -1.0F}}}};

constexpr Vector3 swap_ned_enu(const Vector3& v) noexcept { return kNedEnu * v; }
constexpr Matrix3 swap_ned_enu(const Matrix3& covariance) noexcept {
    return kNedEnu.similarity(covariance);
}

}  // namespace nav
