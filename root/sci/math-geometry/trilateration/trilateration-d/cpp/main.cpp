#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <optional>
#include <cmath>

struct Vec3 {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    [[nodiscard]] constexpr Vec3 operator+(const Vec3& o) const noexcept {
        return {x + o.x, y + o.y, z + o.z};
    }
    [[nodiscard]] constexpr Vec3 operator-(const Vec3& o) const noexcept {
        return {x - o.x, y - o.y, z - o.z};
    }
    [[nodiscard]] constexpr Vec3 operator*(double s) const noexcept {
        return {x * s, y * s, z * s};
    }
    [[nodiscard]] double norm_sq() const noexcept {
        return x * x + y * y + z * z;
    }
    [[nodiscard]] double norm() const noexcept {
        return std::sqrt(norm_sq());
    }
};

struct Anchor {
    Vec3 pos;
    double distance{0.0};
};

struct LocalizationResult {
    Vec3 position;
    double rms_residual{0.0};
};

class TrilaterationSolver {
public:
    /*
     * 3D позиціонування методом лінійних найменших квадратів для N >= 4 маяків
     */
    [[nodiscard]] static std::optional<LocalizationResult> solve_3d(std::span<const Anchor> anchors) noexcept {
        if (anchors.size() < 4) {
            return std::nullopt;
        }

        const auto& a1 = anchors[0];
        const double k1 = a1.pos.norm_sq();
        const double r1_sq = a1.distance * a1.distance;

        // Матриця 3x3 normal equations: AtA
        std::array<std::array<double, 3>, 3> AtA{};
        std::array<double, 3> Atb{};

        for (size_t i = 1; i < anchors.size(); ++i) {
            const auto& ai = anchors[i];
            const double ki = ai.pos.norm_sq();
            const double ri_sq = ai.distance * ai.distance;

            // Рядок лінеаризованої матриці спостережень A
            const std::array<double, 3> row = {
                2.0 * (ai.pos.x - a1.pos.x),
                2.0 * (ai.pos.y - a1.pos.y),
                2.0 * (ai.pos.z - a1.pos.z)
            };

            const double b_val = (r1_sq - ri_sq) + (ki - k1);

            for (size_t r = 0; r < 3; ++r) {
                for (size_t c = 0; c < 3; ++c) {
                    AtA[r][c] += row[r] * row[c];
                }
                Atb[r] += row[r] * b_val;
            }
        }

        const auto inv_AtA = invert_3x3(AtA);
        if (!inv_AtA) {
            return std::nullopt; // Вироджена геометрія
        }

        const auto& inv = *inv_AtA;
        Vec3 estimated_pos{
            inv[0][0] * Atb[0] + inv[0][1] * Atb[1] + inv[0][2] * Atb[2],
            inv[1][0] * Atb[0] + inv[1][1] * Atb[1] + inv[1][2] * Atb[2],
            inv[2][0] * Atb[0] + inv[2][1] * Atb[1] + inv[2][2] * Atb[2]
        };

        // Розрахунок середньоквадратичної похибки (RMS residual)
        double sum_sq_err = 0.0;
        for (const auto& a : anchors) {
            const double d = (estimated_pos - a.pos).norm();
            const double err = d - a.distance;
            sum_sq_err += err * err;
        }

        return LocalizationResult{
            .position = estimated_pos,
            .rms_residual = std::sqrt(sum_sq_err / static_cast<double>(anchors.size()))
        };
    }

private:
    [[nodiscard]] static std::optional<std::array<std::array<double, 3>, 3>>
    invert_3x3(const std::array<std::array<double, 3>, 3>& m) noexcept {
        const double det = m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) -
                           m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0]) +
                           m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]);

        if (std::abs(det) < 1e-12) {
            return std::nullopt;
        }

        const double inv_det = 1.0 / det;
        std::array<std::array<double, 3>, 3> inv{};

        inv[0][0] =  (m[1][1] * m[2][2] - m[1][2] * m[2][1]) * inv_det;
        inv[0][1] = -(m[0][1] * m[2][2] - m[0][2] * m[2][1]) * inv_det;
        inv[0][2] =  (m[0][1] * m[1][2] - m[0][2] * m[1][1]) * inv_det;

        inv[1][0] = -(m[1][0] * m[2][2] - m[1][2] * m[2][0]) * inv_det;
        inv[1][1] =  (m[0][0] * m[2][2] - m[0][2] * m[2][0]) * inv_det;
        inv[1][2] = -(m[0][0] * m[1][2] - m[0][2] * m[1][0]) * inv_det;

        inv[2][0] =  (m[1][0] * m[2][1] - m[1][1] * m[2][0]) * inv_det;
        inv[2][1] = -(m[0][0] * m[2][1] - m[0][1] * m[2][0]) * inv_det;
        inv[2][2] =  (m[0][0] * m[1][1] - m[0][1] * m[1][0]) * inv_det;

        return inv;
    }
};
