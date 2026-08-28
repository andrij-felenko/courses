/*
 * dof_kinematics.cpp - Обчислення кінематики та Якобіана на C++20.
 */

#include <iostream>
#include <array>
#include <span>
#include <cmath>
#include <numbers>
#include <iomanip>

namespace mechanics {

constexpr std::size_t DoF = 6;

struct Vec3 {
    double x{0.0}, y{0.0}, z{0.0};

    [[nodiscard]] constexpr Vec3 cross(const Vec3& o) const noexcept {
        return {
            y * o.z - z * o.y,
            z * o.x - x * o.z,
            x * o.y - y * o.x
        };
    }
};

struct Mat4 {
    std::array<std::array<double, 4>, 4> m{};

    [[nodiscard]] static constexpr Mat4 identity() noexcept {
        Mat4 res{};
        for (std::size_t i = 0; i < 4; ++i) res.m[i][i] = 1.0;
        return res;
    }

    [[nodiscard]] constexpr Mat4 operator*(const Mat4& o) const noexcept {
        Mat4 res{};
        for (std::size_t r = 0; r < 4; ++r) {
            for (std::size_t c = 0; c < 4; ++c) {
                double sum = 0.0;
                for (std::size_t k = 0; k < 4; ++k) sum += m[r][k] * o.m[k][c];
                res.m[r][c] = sum;
            }
        }
        return res;
    }
};

[[nodiscard]] inline Mat4 dh_matrix(double alpha, double a, double d, double theta) noexcept {
    Mat4 res = Mat4::identity();
    const double ct = std::cos(theta), st = std::sin(theta);
    const double ca = std::cos(alpha), sa = std::sin(alpha);

    res.m[0][0] = ct;       res.m[0][1] = -st * ca;  res.m[0][2] = st * sa;   res.m[0][3] = a * ct;
    res.m[1][0] = st;       res.m[1][1] = ct * ca;   res.m[1][2] = -ct * sa;  res.m[1][3] = a * st;
    res.m[2][0] = 0.0;      res.m[2][1] = sa;        res.m[2][2] = ca;        res.m[2][3] = d;
    res.m[3][0] = 0.0;      res.m[3][1] = 0.0;       res.m[3][2] = 0.0;       res.m[3][3] = 1.0;

    return res;
}

struct KinematicsResult {
    Mat4 end_effector_transform;
    std::array<std::array<double, DoF>, 6> jacobian{};
};

[[nodiscard]] KinematicsResult forward_kinematics_and_jacobian(std::span<const double, DoF> q) noexcept {
    constexpr std::array<double, DoF> alpha{
        std::numbers::pi / 2.0, 0.0, std::numbers::pi / 2.0,
        -std::numbers::pi / 2.0, std::numbers::pi / 2.0, 0.0
    };
    constexpr std::array<double, DoF> a{ 0.0, 0.432, 0.020, 0.0, 0.0, 0.0 };
    constexpr std::array<double, DoF> d{ 0.150, 0.0, 0.0, 0.432, 0.0, 0.050 };

    std::array<Mat4, DoF + 1> T{};
    T[0] = Mat4::identity();

    std::array<Vec3, DoF> z_axes{};
    std::array<Vec3, DoF> p_origins{};

    for (std::size_t i = 0; i < DoF; ++i) {
        Mat4 A_i = dh_matrix(alpha[i], a[i], d[i], q[i]);
        T[i + 1] = T[i] * A_i;

        z_axes[i] = {T[i].m[0][2], T[i].m[1][2], T[i].m[2][2]};
        p_origins[i] = {T[i].m[0][3], T[i].m[1][3], T[i].m[2][3]};
    }

    const Vec3 p_end{T[DoF].m[0][3], T[DoF].m[1][3], T[DoF].m[2][3]};
    std::array<std::array<double, DoF>, 6> J{};

    for (std::size_t i = 0; i < DoF; ++i) {
        const Vec3 r{p_end.x - p_origins[i].x, p_end.y - p_origins[i].y, p_end.z - p_origins[i].z};
        const Vec3 lin = z_axes[i].cross(r);

        J[0][i] = z_axes[i].x;
        J[1][i] = z_axes[i].y;
        J[2][i] = z_axes[i].z;
        J[3][i] = lin.x;
        J[4][i] = lin.y;
        J[5][i] = lin.z;
    }

    return {T[DoF], J};
}

} // namespace mechanics

int main() {
    const std::array<double, mechanics::DoF> q{0.1, 0.3, -0.5, 0.2, 0.4, -0.1};
    const auto [T_end, J] = mechanics::forward_kinematics_and_jacobian(q);

    std::cout << "=== Пряма кінематика 6-DoF маніпулятора (C++20) ===\n";
    std::cout << "Положення схоплювача: x = " << std::fixed << std::setprecision(3)
              << T_end.m[0][3] << " м, y = " << T_end.m[1][3] << " м, z = " << T_end.m[2][3] << " м\n\n";

    std::cout << "Матриця Якобі J(q) розмірності 6x6:\n";
    for (const auto& row : J) {
        for (double val : row) {
            std::cout << std::setw(8) << std::setprecision(3) << val << " ";
        }
        std::cout << "\n";
    }

    return 0;
}
