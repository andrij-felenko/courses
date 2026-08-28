#include <array>
#include <cmath>
#include <optional>
#include <span>
#include <algorithm>

namespace drone::robotics {

constexpr std::size_t kDof = 6;
constexpr std::size_t kCartesianDim = 6;

using Matrix6d = std::array<std::array<double, kDof>, kCartesianDim>;
using Vector6d = std::array<double, kDof>;

struct Twist {
    std::array<double, 3> linear{};   // Швидкість поступального руху (м/с)
    std::array<double, 3> angular{};  // Кутова швидкість (рад/с)
};

struct DlsSettings {
    double lambda_max{0.3};           // Максимальний коефіцієнт демпфування
    double w_threshold{0.05};         // Поріг маніпулятивності Йошікави
    double max_joint_vel{5.0};        // Максимальна кутова швидкість суглоба (рад/с)
};

class SingularityRobustSolver {
public:
    explicit constexpr SingularityRobustSolver(DlsSettings settings = {})
        : settings_{settings} {}

    [[nodiscard]] static double computeManipulability(const Matrix6d& jacobian) noexcept {
        const auto gram = computeGram(jacobian);
        const auto det = computeDeterminant6x6(gram);
        return (det > 0.0) ? std::sqrt(det) : 0.0;
    }

    [[nodiscard]] std::optional<Vector6d> solveVelocityIk(
        const Matrix6d& jacobian,
        const Twist& target_twist) const noexcept {

        auto gram = computeGram(jacobian);
        const double w = computeManipulability(jacobian);

        // Адаптивне квадратичне демпфування
        double lambda_sq = 0.0;
        if (w < settings_.w_threshold) {
            const double ratio = 1.0 - (w / settings_.w_threshold);
            lambda_sq = settings_.lambda_max * settings_.lambda_max * ratio * ratio;
        }

        // Регуляризація діагоналі G + lambda^2 * I
        for (std::size_t i = 0; i < kCartesianDim; ++i) {
            gram[i][i] += lambda_sq;
        }

        const auto gram_inv = invertMatrix6x6(gram);
        if (!gram_inv) {
            return std::nullopt;
        }

        const std::array<double, kCartesianDim> x_dot{
            target_twist.linear[0],  target_twist.linear[1],  target_twist.linear[2],
            target_twist.angular[0], target_twist.angular[1], target_twist.angular[2]
        };

        // v_temp = (J * J^T + lambda^2 * I)^(-1) * x_dot
        std::array<double, kCartesianDim> v_temp{};
        for (std::size_t r = 0; r < kCartesianDim; ++r) {
            for (std::size_t c = 0; c < kCartesianDim; ++c) {
                v_temp[r] += (*gram_inv)[r][c] * x_dot[c];
            }
        }

        // q_dot = J^T * v_temp
        Vector6d q_dot{};
        double max_vel = 0.0;
        for (std::size_t j = 0; j < kDof; ++j) {
            for (std::size_t r = 0; r < kCartesianDim; ++r) {
                q_dot[j] += jacobian[r][j] * v_temp[r];
            }
            max_vel = std::max(max_vel, std::abs(q_dot[j]));
        }

        // Пропорційне насичення швидкостей суглобів
        if (max_vel > settings_.max_joint_vel && max_vel > 1e-6) {
            const double scale = settings_.max_joint_vel / max_vel;
            for (auto& vel : q_dot) {
                vel *= scale;
            }
        }

        return q_dot;
    }

private:
    DlsSettings settings_;

    [[nodiscard]] static Matrix6d computeGram(const Matrix6d& j) noexcept {
        Matrix6d g{};
        for (std::size_t r = 0; r < kCartesianDim; ++r) {
            for (std::size_t c = 0; c < kCartesianDim; ++c) {
                double sum = 0.0;
                for (std::size_t k = 0; k < kDof; ++k) {
                    sum += j[r][k] * j[c][k];
                }
                g[r][c] = sum;
            }
        }
        return g;
    }

    [[nodiscard]] static double computeDeterminant6x6(Matrix6d mat) noexcept {
        double det = 1.0;
        for (std::size_t i = 0; i < kCartesianDim; ++i) {
            std::size_t pivot = i;
            double max_val = std::abs(mat[i][i]);
            for (std::size_t r = i + 1; r < kCartesianDim; ++r) {
                if (const double val = std::abs(mat[r][i]); val > max_val) {
                    max_val = val;
                    pivot = r;
                }
            }

            if (max_val < 1e-12) return 0.0;

            if (pivot != i) {
                std::swap(mat[i], mat[pivot]);
                det = -det;
            }

            const double diag = mat[i][i];
            det *= diag;

            for (std::size_t r = i + 1; r < kCartesianDim; ++r) {
                const double factor = mat[r][i] / diag;
                for (std::size_t c = i; c < kCartesianDim; ++c) {
                    mat[r][c] -= factor * mat[i][c];
                }
            }
        }
        return det;
    }

    [[nodiscard]] static std::optional<Matrix6d> invertMatrix6x6(const Matrix6d& in) noexcept {
        std::array<std::array<double, 12>, 6> aug{};
        for (std::size_t r = 0; r < 6; ++r) {
            for (std::size_t c = 0; c < 6; ++c) {
                aug[r][c] = in[r][c];
                aug[r][c + 6] = (r == c) ? 1.0 : 0.0;
            }
        }

        for (std::size_t i = 0; i < 6; ++i) {
            std::size_t pivot = i;
            double max_val = std::abs(aug[i][i]);
            for (std::size_t r = i + 1; r < 6; ++r) {
                if (const double val = std::abs(aug[r][i]); val > max_val) {
                    max_val = val;
                    pivot = r;
                }
            }

            if (max_val < 1e-12) return std::nullopt;

            if (pivot != i) {
                std::swap(aug[i], aug[pivot]);
            }

            const double diag = aug[i][i];
            for (std::size_t c = 0; c < 12; ++c) {
                aug[i][c] /= diag;
            }

            for (std::size_t r = 0; r < 6; ++r) {
                if (r != i) {
                    const double factor = aug[r][i];
                    for (std::size_t c = 0; c < 12; ++c) {
                        aug[r][c] -= factor * aug[i][c];
                    }
                }
            }
        }

        Matrix6d inv{};
        for (std::size_t r = 0; r < 6; ++r) {
            for (std::size_t c = 0; c < 6; ++c) {
                inv[r][c] = aug[r][c + 6];
            }
        }
        return inv;
    }
};

} // namespace drone::robotics
