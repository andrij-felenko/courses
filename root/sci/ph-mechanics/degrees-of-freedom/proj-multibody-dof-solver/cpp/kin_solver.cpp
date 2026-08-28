/*
 * kin_solver.cpp - Високопродуктивний кінематичний розв'язувач на C++20.
 * Використовує std::span, концептуальні шаблони, constexpr матриці,
 * структуровані прив'язки та типізовані перетворення SE(3).
 */

#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <cmath>
#include <numbers>
#include <algorithm>
#include <iomanip>
#include <string_view>
#include <expected>

namespace kin {

constexpr std::size_t TaskDim = 6;
constexpr double EpsilonTol = 1e-12;
constexpr std::size_t SvdMaxIterations = 100;

enum class JointType {
    Revolute,
    Prismatic
};

struct Vec3 {
    double x{0.0}, y{0.0}, z{0.0};

    [[nodiscard]] constexpr Vec3 operator+(const Vec3& o) const noexcept {
        return {x + o.x, y + o.y, z + o.z};
    }
    [[nodiscard]] constexpr Vec3 operator-(const Vec3& o) const noexcept {
        return {x - o.x, y - o.y, z - o.z};
    }
    [[nodiscard]] constexpr Vec3 operator*(double s) const noexcept {
        return {x * s, y * s, z * s};
    }
    [[nodiscard]] constexpr double dot(const Vec3& o) const noexcept {
        return x * o.x + y * o.y + z * o.z;
    }
    [[nodiscard]] constexpr Vec3 cross(const Vec3& o) const noexcept {
        return {
            y * o.z - z * o.y,
            z * o.x - x * o.z,
            x * o.y - y * o.x
        };
    }
    [[nodiscard]] double norm() const noexcept {
        return std::sqrt(dot(*this));
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
                for (std::size_t k = 0; k < 4; ++k) {
                    sum += m[r][k] * o.m[k][c];
                }
                res.m[r][c] = sum;
            }
        }
        return res;
    }

    [[nodiscard]] constexpr Vec3 transform_point(const Vec3& p) const noexcept {
        return {
            m[0][0] * p.x + m[0][1] * p.y + m[0][2] * p.z + m[0][3],
            m[1][0] * p.x + m[1][1] * p.y + m[1][2] * p.z + m[1][3],
            m[2][0] * p.x + m[2][1] * p.y + m[2][2] * p.z + m[2][3]
        };
    }

    [[nodiscard]] constexpr Vec3 transform_vector(const Vec3& v) const noexcept {
        return {
            m[0][0] * v.x + m[0][1] * v.y + m[0][2] * v.z,
            m[1][0] * v.x + m[1][1] * v.y + m[1][2] * v.z,
            m[2][0] * v.x + m[2][1] * v.y + m[2][2] * v.z
        };
    }
};

struct Joint {
    JointType type{JointType::Revolute};
    Vec3 axis{0.0, 0.0, 1.0};
    Mat4 offset{Mat4::identity()};
    double q_min{-std::numbers::pi};
    double q_max{std::numbers::pi};
    double q_rest{0.0};
};

struct SvdResult {
    std::vector<double> singular_values;
    std::vector<std::vector<double>> U;
    std::vector<std::vector<double>> V;
    std::size_t rank{0};
    double manipulability{0.0};
    double condition_number{1.0};
};

class KinematicSolver {
public:
    explicit KinematicSolver(std::vector<Joint> joints)
        : joints_(std::move(joints)) {}

    [[nodiscard]] std::size_t num_joints() const noexcept {
        return joints_.size();
    }

    [[nodiscard]] std::pair<Mat4, std::vector<std::array<double, TaskDim>>>
    forward_kinematics_and_jacobian(std::span<const double> q) const {
        const std::size_t n = joints_.size();
        Mat4 T_curr = Mat4::identity();
        std::vector<Mat4> T_frames;
        T_frames.reserve(n + 1);
        T_frames.push_back(T_curr);

        std::vector<Vec3> z_axes;
        std::vector<Vec3> p_origins;
        z_axes.reserve(n);
        p_origins.reserve(n);

        for (std::size_t i = 0; i < n; ++i) {
            Mat4 T_j = joint_transform(joints_[i].type, joints_[i].axis, q[i]);
            T_curr = T_curr * joints_[i].offset * T_j;
            T_frames.push_back(T_curr);

            z_axes.push_back(T_frames[i].transform_vector(joints_[i].axis));
            p_origins.push_back(T_frames[i].transform_point({0, 0, 0}));
        }

        const Vec3 p_end = T_curr.transform_point({0, 0, 0});
        std::vector<std::array<double, TaskDim>> J_cols(n);

        for (std::size_t i = 0; i < n; ++i) {
            if (joints_[i].type == JointType::Revolute) {
                const Vec3 rot_axis = z_axes[i];
                const Vec3 lin_vel = rot_axis.cross(p_end - p_origins[i]);
                J_cols[i] = {rot_axis.x, rot_axis.y, rot_axis.z, lin_vel.x, lin_vel.y, lin_vel.z};
            } else {
                const Vec3 trans_axis = z_axes[i];
                J_cols[i] = {0.0, 0.0, 0.0, trans_axis.x, trans_axis.y, trans_axis.z};
            }
        }

        return {T_curr, J_cols};
    }

    [[nodiscard]] SvdResult analyze_jacobian(
        const std::vector<std::array<double, TaskDim>>& J_cols) const
    {
        const std::size_t n = J_cols.size();
        const std::size_t m = TaskDim;

        std::vector<std::vector<double>> work_A(m, std::vector<double>(n));
        for (std::size_t c = 0; c < n; ++c) {
            for (std::size_t r = 0; r < m; ++r) {
                work_A[r][c] = J_cols[c][r];
            }
        }

        std::vector<std::vector<double>> V(n, std::vector<double>(n, 0.0));
        for (std::size_t i = 0; i < n; ++i) V[i][i] = 1.0;

        for (std::size_t iter = 0; iter < SvdMaxIterations; ++iter) {
            double max_err = 0.0;
            for (std::size_t i = 0; i < n - 1; ++i) {
                for (std::size_t j = i + 1; j < n; ++j) {
                    double a = 0.0, b = 0.0, c = 0.0;
                    for (std::size_t k = 0; k < m; ++k) {
                        a += work_A[k][i] * work_A[k][i];
                        b += work_A[k][j] * work_A[k][j];
                        c += work_A[k][i] * work_A[k][j];
                    }
                    max_err = std::max(max_err, std::abs(c));

                    if (std::abs(c) > 1e-15) {
                        const double zeta = (b - a) / (2.0 * c);
                        const double t = (zeta >= 0.0 ? 1.0 : -1.0) / (std::abs(zeta) + std::sqrt(1.0 + zeta * zeta));
                        const double cos_v = 1.0 / std::sqrt(1.0 + t * t);
                        const double sin_v = t * cos_v;

                        for (std::size_t k = 0; k < m; ++k) {
                            const double temp_i = work_A[k][i];
                            const double temp_j = work_A[k][j];
                            work_A[k][i] = cos_v * temp_i - sin_v * temp_j;
                            work_A[k][j] = sin_v * temp_i + cos_v * temp_j;
                        }

                        for (std::size_t k = 0; k < n; ++k) {
                            const double temp_i = V[k][i];
                            const double temp_j = V[k][j];
                            V[k][i] = cos_v * temp_i - sin_v * temp_j;
                            V[k][j] = sin_v * temp_i + cos_v * temp_j;
                        }
                    }
                }
            }
            if (max_err < 1e-13) break;
        }

        const std::size_t min_dim = std::min(m, n);
        std::vector<double> S(min_dim);
        std::vector<std::vector<double>> U(m, std::vector<double>(min_dim, 0.0));

        for (std::size_t i = 0; i < min_dim; ++i) {
            double norm = 0.0;
            for (std::size_t k = 0; k < m; ++k) norm += work_A[k][i] * work_A[k][i];
            S[i] = std::sqrt(norm);
            if (S[i] > 1e-14) {
                for (std::size_t k = 0; k < m; ++k) U[k][i] = work_A[k][i] / S[i];
            }
        }

        for (std::size_t i = 0; i < min_dim - 1; ++i) {
            for (std::size_t j = i + 1; j < min_dim; ++j) {
                if (S[j] > S[i]) {
                    std::swap(S[i], S[j]);
                    for (std::size_t k = 0; k < m; ++k) std::swap(U[k][i], U[k][j]);
                    for (std::size_t k = 0; k < n; ++k) std::swap(V[k][i], V[k][j]);
                }
            }
        }

        const double s_max = S.front();
        const double s_min = S.back();
        const double tol = std::max(EpsilonTol, static_cast<double>(std::max(m, n)) * s_max * 2.22e-16);

        std::size_t rk = 0;
        double manip = 1.0;
        for (double s : S) {
            if (s > tol) {
                rk++;
                manip *= s;
            }
        }

        return SvdResult{
            .singular_values = std::move(S),
            .U = std::move(U),
            .V = std::move(V),
            .rank = rk,
            .manipulability = (rk == min_dim ? manip : 0.0),
            .condition_number = (s_min > 1e-12 ? s_max / s_min : 1e12)
        };
    }

    [[nodiscard]] std::vector<double> solve_ik_dls(
        const std::vector<std::array<double, TaskDim>>& J_cols,
        std::span<const double, TaskDim> twist_cmd,
        std::span<const double> q_curr,
        double lambda_max,
        double w_threshold,
        const SvdResult& svd) const
    {
        const std::size_t n = joints_.size();
        const std::size_t m = TaskDim;

        double lambda = 0.0;
        if (svd.manipulability < w_threshold) {
            const double r = 1.0 - (svd.manipulability / w_threshold);
            lambda = lambda_max * r * r;
        }
        const double lambda_sq = lambda * lambda;

        std::array<std::array<double, TaskDim>, TaskDim> A{};
        for (std::size_t r = 0; r < m; ++r) {
            for (std::size_t c = 0; c < m; ++c) {
                double sum = 0.0;
                for (std::size_t k = 0; k < n; ++k) sum += J_cols[k][r] * J_cols[k][c];
                A[r][c] = sum;
            }
            A[r][r] += lambda_sq;
        }

        std::array<std::array<double, TaskDim + 1>, TaskDim> aug{};
        for (std::size_t r = 0; r < m; ++r) {
            for (std::size_t c = 0; c < m; ++c) aug[r][c] = A[r][c];
            aug[r][m] = twist_cmd[r];
        }

        for (std::size_t k = 0; k < m; ++k) {
            std::size_t max_r = k;
            double max_val = std::abs(aug[k][k]);
            for (std::size_t r = k + 1; r < m; ++r) {
                if (std::abs(aug[r][k]) > max_val) {
                    max_val = std::abs(aug[r][k]);
                    max_r = r;
                }
            }
            if (max_r != k) std::swap(aug[k], aug[max_r]);

            double pivot = aug[k][k];
            if (std::abs(pivot) < 1e-14) pivot = (pivot >= 0.0 ? 1e-14 : -1e-14);

            for (std::size_t r = k + 1; r < m; ++r) {
                const double factor = aug[r][k] / pivot;
                for (std::size_t c = k; c <= m; ++c) aug[r][c] -= factor * aug[k][c];
            }
        }

        std::array<double, TaskDim> f{};
        for (int r = static_cast<int>(m) - 1; r >= 0; --r) {
            double sum = aug[r][m];
            for (std::size_t c = r + 1; c < m; ++c) sum -= aug[r][c] * f[c];
            f[r] = sum / aug[r][r];
        }

        std::vector<double> q_dot(n, 0.0);
        for (std::size_t i = 0; i < n; ++i) {
            double sum = 0.0;
            for (std::size_t r = 0; r < m; ++r) sum += J_cols[i][r] * f[r];
            q_dot[i] = sum;
        }

        std::vector<double> q_null_des(n);
        constexpr double k_null = 2.0;
        for (std::size_t i = 0; i < n; ++i) {
            q_null_des[i] = -k_null * (q_curr[i] - joints_[i].q_rest);
        }

        std::array<double, TaskDim> J_qnull{};
        for (std::size_t r = 0; r < m; ++r) {
            for (std::size_t c = 0; c < n; ++c) J_qnull[r] += J_cols[c][r] * q_null_des[c];
        }

        for (std::size_t r = 0; r < m; ++r) {
            for (std::size_t c = 0; c < m; ++c) aug[r][c] = A[r][c];
            aug[r][m] = J_qnull[r];
        }

        for (std::size_t k = 0; k < m; ++k) {
            double pivot = aug[k][k];
            if (std::abs(pivot) < 1e-14) pivot = (pivot >= 0.0 ? 1e-14 : -1e-14);
            for (std::size_t r = k + 1; r < m; ++r) {
                const double factor = aug[r][k] / pivot;
                for (std::size_t c = k; c <= m; ++c) aug[r][c] -= factor * aug[k][c];
            }
        }

        std::array<double, TaskDim> f_null{};
        for (int r = static_cast<int>(m) - 1; r >= 0; --r) {
            double sum = aug[r][m];
            for (std::size_t c = r + 1; c < m; ++c) sum -= aug[r][c] * f_null[c];
            f_null[r] = sum / aug[r][r];
        }

        for (std::size_t i = 0; i < n; ++i) {
            double Jt_f = 0.0;
            for (std::size_t r = 0; r < m; ++r) Jt_f += J_cols[i][r] * f_null[r];
            q_dot[i] += (q_null_des[i] - Jt_f);
        }

        return q_dot;
    }

private:
    static Mat4 joint_transform(JointType type, const Vec3& axis, double q) noexcept {
        Mat4 res = Mat4::identity();
        if (type == JointType::Revolute) {
            const double c = std::cos(q);
            const double s = std::sin(q);
            const double v = 1.0 - c;
            const auto [kx, ky, kz] = axis;

            res.m[0][0] = kx * kx * v + c;
            res.m[0][1] = kx * ky * v - kz * s;
            res.m[0][2] = kx * kz * v + ky * s;

            res.m[1][0] = kx * ky * v + kz * s;
            res.m[1][1] = ky * ky * v + c;
            res.m[1][2] = ky * kz * v - kx * s;

            res.m[2][0] = kx * kz * v - ky * s;
            res.m[2][1] = ky * kz * v + kx * s;
            res.m[2][2] = kz * kz * v + c;
        } else {
            res.m[0][3] = axis.x * q;
            res.m[1][3] = axis.y * q;
            res.m[2][3] = axis.z * q;
        }
        return res;
    }

    std::vector<Joint> joints_;
};

} // namespace kin

int main() {
    std::vector<kin::Joint> joints(6);
    for (auto& j : joints) {
        j.type = kin::JointType::Revolute;
        j.axis = {0.0, 0.0, 1.0};
        j.offset = kin::Mat4::identity();
    }

    joints[0].offset.m[2][3] = 0.3;
    joints[1].axis = {0.0, 1.0, 0.0};
    joints[2].axis = {0.0, 1.0, 0.0};
    joints[2].offset.m[2][3] = 0.4;
    joints[3].axis = {1.0, 0.0, 0.0};
    joints[3].offset.m[2][3] = 0.4;
    joints[4].axis = {0.0, 1.0, 0.0};
    joints[5].axis = {0.0, 0.0, 1.0};
    joints[5].offset.m[2][3] = 0.15;

    kin::KinematicSolver solver(std::move(joints));

    const std::array<double, 6> q_normal{0.2, 0.5, -0.8, 0.1, 0.4, -0.2};
    const std::array<double, 6> q_singular{0.0, 0.0, 0.0, 0.0, 0.0, 0.0};

    std::cout << "=== Демонстрація кінематичного розв'язувача (C++20) ===\n\n";

    const auto [T_normal, J_normal] = solver.forward_kinematics_and_jacobian(q_normal);
    const auto svd_normal = solver.analyze_jacobian(J_normal);

    std::cout << "1. Звичайна конфігурація:\n";
    std::cout << "   Положення: (" << std::fixed << std::setprecision(3)
              << T_normal.m[0][3] << ", " << T_normal.m[1][3] << ", " << T_normal.m[2][3] << ") м\n";
    std::cout << "   Сингулярні числа: ";
    for (double s : svd_normal.singular_values) std::cout << s << " ";
    std::cout << "\n   Ранг: " << svd_normal.rank << " / 6, Маніпулятивність: "
              << std::scientific << svd_normal.manipulability
              << ", kappa(J): " << std::fixed << svd_normal.condition_number << "\n\n";

    const auto [T_sing, J_sing] = solver.forward_kinematics_and_jacobian(q_singular);
    const auto svd_sing = solver.analyze_jacobian(J_sing);

    std::cout << "2. Сингулярна конфігурація:\n";
    std::cout << "   Положення: (" << std::fixed << std::setprecision(3)
              << T_sing.m[0][3] << ", " << T_sing.m[1][3] << ", " << T_sing.m[2][3] << ") м\n";
    std::cout << "   Сингулярні числа: ";
    for (double s : svd_sing.singular_values) std::cout << std::scientific << s << " ";
    std::cout << "\n   Ранг: " << svd_sing.rank << " / 6, Маніпулятивність: "
              << svd_sing.manipulability << ", kappa(J): " << svd_sing.condition_number << "\n\n";

    const std::array<double, 6> twist_cmd{0.0, 0.0, 0.0, 0.0, 0.0, 0.2};
    const auto q_dot = solver.solve_ik_dls(J_sing, twist_cmd, q_singular, 0.1, 0.05, svd_sing);

    std::cout << "3. Швидкості шарнірів DLS (рад/с): ";
    for (double v : q_dot) std::cout << std::fixed << std::setprecision(4) << v << " ";
    std::cout << "\n";

    return 0;
}
