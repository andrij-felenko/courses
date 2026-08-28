#include <iostream>
#include <vector>
#include <span>
#include <array>
#include <cmath>
#include <optional>
#include <algorithm>
#include <numeric>

struct Point2D {
    double x{0.0};
    double y{0.0};
};

struct Mat3x3 {
    std::array<std::array<double, 3>, 3> m{};

    [[nodiscard]] constexpr double at(size_t r, size_t c) const noexcept { return m[r][c]; }
    constexpr double& at(size_t r, size_t c) noexcept { return m[r][c]; }

    [[nodiscard]] Mat3x3 operator*(const Mat3x3& rhs) const noexcept {
        Mat3x3 res{};
        for (size_t r = 0; r < 3; ++r) {
            for (size_t c = 0; c < 3; ++c) {
                res.m[r][c] = m[r][0] * rhs.m[0][c] +
                              m[r][1] * rhs.m[1][c] +
                              m[r][2] * rhs.m[2][c];
            }
        }
        return res;
    }
};

class HomographyEstimator {
public:
    [[nodiscard]] static std::optional<Mat3x3> estimateDLT(
        std::span<const Point2D> src,
        std::span<const Point2D> dst) noexcept 
    {
        if (src.size() != dst.size() || src.size() < 4) {
            return std::nullopt;
        }

        const size_t n = src.size();
        const auto T_src = computeHartleyTransform(src);
        const auto T_dst = computeHartleyTransform(dst);

        // Формування нормальних рівнянь M = A^T * A розміром 9x9
        std::array<std::array<double, 9>, 9> M{};

        for (size_t i = 0; i < n; ++i) {
            const double x = T_src.at(0, 0) * src[i].x + T_src.at(0, 2);
            const double y = T_src.at(1, 1) * src[i].y + T_src.at(1, 2);
            const double u = T_dst.at(0, 0) * dst[i].x + T_dst.at(0, 2);
            const double v = T_dst.at(1, 1) * dst[i].y + T_dst.at(1, 2);

            const std::array<double, 9> r1 = { 0.0, 0.0, 0.0, -x, -y, -1.0, v * x, v * y, v };
            const std::array<double, 9> r2 = { x, y, 1.0, 0.0, 0.0, 0.0, -u * x, -u * y, -u };

            for (size_t r = 0; r < 9; ++r) {
                for (size_t c = 0; c < 9; ++c) {
                    M[r][c] += r1[r] * r1[c] + r2[r] * r2[c];
                }
            }
        }

        auto V = solveJacobiEigensystem(M);

        // Пошук стовпця з мінімальним власним числом
        size_t min_col = 0;
        double min_eval = 1e30;
        for (size_t col = 0; col < 9; ++col) {
            double eval = 0.0;
            for (size_t r = 0; r < 9; ++r) {
                double sum = 0.0;
                for (size_t k = 0; k < 9; ++k) sum += M[r][k] * V[k][col];
                eval += V[r][col] * sum;
            }
            if (eval < min_eval) {
                min_eval = eval;
                min_col = col;
            }
        }

        Mat3x3 H_norm{};
        H_norm.at(0, 0) = V[0][min_col]; H_norm.at(0, 1) = V[1][min_col]; H_norm.at(0, 2) = V[2][min_col];
        H_norm.at(1, 0) = V[3][min_col]; H_norm.at(1, 1) = V[4][min_col]; H_norm.at(1, 2) = V[5][min_col];
        H_norm.at(2, 0) = V[6][min_col]; H_norm.at(2, 1) = V[7][min_col]; H_norm.at(2, 2) = V[8][min_col];

        // Денормалізація: H = inv(T_dst) * H_norm * T_src
        const auto inv_T_dst = invertHartley(T_dst);
        Mat3x3 H = inv_T_dst * H_norm * T_src;

        if (std::abs(H.at(2, 2)) > 1e-12) {
            const double inv_h33 = 1.0 / H.at(2, 2);
            for (size_t r = 0; r < 3; ++r) {
                for (size_t c = 0; c < 3; ++c) {
                    H.at(r, c) *= inv_h33;
                }
            }
        }

        return H;
    }

private:
    [[nodiscard]] static Mat3x3 computeHartleyTransform(std::span<const Point2D> pts) noexcept {
        const double inv_n = 1.0 / static_cast<double>(pts.size());
        double sum_x = 0.0, sum_y = 0.0;
        for (const auto& p : pts) {
            sum_x += p.x;
            sum_y += p.y;
        }
        const double mean_x = sum_x * inv_n;
        const double mean_y = sum_y * inv_n;

        double dist_sum = 0.0;
        for (const auto& p : pts) {
            dist_sum += std::hypot(p.x - mean_x, p.y - mean_y);
        }
        const double mean_dist = dist_sum * inv_n;
        const double scale = (mean_dist > 1e-12) ? (std::numbers::sqrt2 / mean_dist) : 1.0;

        Mat3x3 T{};
        T.at(0, 0) = scale; T.at(0, 2) = -scale * mean_x;
        T.at(1, 1) = scale; T.at(1, 2) = -scale * mean_y;
        T.at(2, 2) = 1.0;
        return T;
    }

    [[nodiscard]] static Mat3x3 invertHartley(const Mat3x3& T) noexcept {
        const double scale = T.at(0, 0);
        const double mean_x = -T.at(0, 2) / scale;
        const double mean_y = -T.at(1, 2) / scale;

        Mat3x3 inv{};
        inv.at(0, 0) = 1.0 / scale; inv.at(0, 2) = mean_x;
        inv.at(1, 1) = 1.0 / scale; inv.at(1, 2) = mean_y;
        inv.at(2, 2) = 1.0;
        return inv;
    }

    [[nodiscard]] static std::array<std::array<double, 9>, 9> solveJacobiEigensystem(
        std::array<std::array<double, 9>, 9> A) noexcept 
    {
        std::array<std::array<double, 9>, 9> V{};
        for (size_t i = 0; i < 9; ++i) V[i][i] = 1.0;

        constexpr size_t max_iter = 50;
        for (size_t iter = 0; iter < max_iter; ++iter) {
            double max_off = 0.0;
            size_t p = 0, q = 1;
            for (size_t i = 0; i < 9; ++i) {
                for (size_t j = i + 1; j < 9; ++j) {
                    const double val = std::abs(A[i][j]);
                    if (val > max_off) {
                        max_off = val;
                        p = i;
                        q = j;
                    }
                }
            }
            if (max_off < 1e-15) break;

            const double theta = 0.5 * (A[q][q] - A[p][p]) / A[p][q];
            double t = 1.0 / (std::abs(theta) + std::sqrt(theta * theta + 1.0));
            if (theta < 0.0) t = -t;

            const double c = 1.0 / std::sqrt(t * t + 1.0);
            const double s = t * c;
            const double tau = s / (1.0 + c);

            const double app = A[p][p];
            const double aqq = A[q][q];
            const double apq = A[p][q];

            A[p][p] = app - t * apq;
            A[q][q] = aqq + t * apq;
            A[p][q] = 0.0;
            A[q][p] = 0.0;

            for (size_t k = 0; k < 9; ++k) {
                if (k != p && k != q) {
                    const double akp = A[k][p];
                    const double akq = A[k][q];
                    A[k][p] = akp - s * (akq + tau * akp);
                    A[p][k] = A[k][p];
                    A[k][q] = akq + s * (akp - tau * akq);
                    A[q][k] = A[k][q];
                }
            }

            for (size_t k = 0; k < 9; ++k) {
                const double vkp = V[k][p];
                const double vkq = V[k][q];
                V[k][p] = vkp - s * (vkq + tau * vkp);
                V[k][q] = vkq + s * (vkp - tau * vkq);
            }
        }
        return V;
    }
};
