#include <iostream>
#include <vector>
#include <span>
#include <array>
#include <cmath>
#include <optional>
#include <expected>
#include <numbers>
#include <algorithm>
#include <numeric>
#include <random>
#include <iomanip>

namespace vision::geometry {

struct Point2D {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] constexpr bool operator==(const Point2D& other) const noexcept = default;
};

class Matrix3x3 {
public:
    std::array<std::array<double, 3>, 3> data{};

    [[nodiscard]] constexpr double at(size_t r, size_t c) const noexcept { return data[r][c]; }
    constexpr double& at(size_t r, size_t c) noexcept { return data[r][c]; }

    [[nodiscard]] constexpr static Matrix3x3 identity() noexcept {
        Matrix3x3 I{};
        I.data[0][0] = 1.0; I.data[1][1] = 1.0; I.data[2][2] = 1.0;
        return I;
    }

    [[nodiscard]] constexpr double determinant() const noexcept {
        return data[0][0] * (data[1][1] * data[2][2] - data[1][2] * data[2][1]) -
               data[0][1] * (data[1][0] * data[2][2] - data[1][2] * data[2][0]) +
               data[0][2] * (data[1][0] * data[2][1] - data[1][1] * data[2][0]);
    }

    [[nodiscard]] std::optional<Matrix3x3> inverse() const noexcept {
        const double det = determinant();
        if (std::abs(det) < 1e-12) return std::nullopt;
        const double inv_det = 1.0 / det;

        Matrix3x3 inv{};
        inv.data[0][0] = (data[1][1] * data[2][2] - data[1][2] * data[2][1]) * inv_det;
        inv.data[0][1] = (data[0][2] * data[2][1] - data[0][1] * data[2][2]) * inv_det;
        inv.data[0][2] = (data[0][1] * data[1][2] - data[0][2] * data[1][1]) * inv_det;

        inv.data[1][0] = (data[1][2] * data[2][0] - data[1][0] * data[2][2]) * inv_det;
        inv.data[1][1] = (data[0][0] * data[2][2] - data[0][2] * data[2][0]) * inv_det;
        inv.data[1][2] = (data[0][2] * data[1][0] - data[0][0] * data[1][2]) * inv_det;

        inv.data[2][0] = (data[1][0] * data[2][1] - data[1][1] * data[2][0]) * inv_det;
        inv.data[2][1] = (data[0][1] * data[2][0] - data[0][0] * data[2][1]) * inv_det;
        inv.data[2][2] = (data[0][0] * data[1][1] - data[0][1] * data[1][0]) * inv_det;

        return inv;
    }

    [[nodiscard]] Matrix3x3 operator*(const Matrix3x3& rhs) const noexcept {
        Matrix3x3 res{};
        for (size_t r = 0; r < 3; ++r) {
            for (size_t c = 0; c < 3; ++c) {
                res.data[r][c] = data[r][0] * rhs.data[0][c] +
                                 data[r][1] * rhs.data[1][c] +
                                 data[r][2] * rhs.data[2][c];
            }
        }
        return res;
    }

    [[nodiscard]] std::optional<Point2D> transform(const Point2D& pt) const noexcept {
        const double z = data[2][0] * pt.x + data[2][1] * pt.y + data[2][2];
        if (std::abs(z) < 1e-12) return std::nullopt;
        const double inv_z = 1.0 / z;
        return Point2D{
            (data[0][0] * pt.x + data[0][1] * pt.y + data[0][2]) * inv_z,
            (data[1][0] * pt.x + data[1][1] * pt.y + data[1][2]) * inv_z
        };
    }
};

struct RansacConfig {
    double max_reprojection_error{2.5};
    size_t max_iterations{1000};
    double confidence{0.999};
};

struct EstimationResult {
    Matrix3x3 H{};
    size_t inlier_count{0};
    std::vector<bool> inlier_mask{};
    double mean_reprojection_error{0.0};
};

enum class EstimationError {
    InsufficientPoints,
    CollinearDegeneracy,
    NoConsensusFound,
    InversionFailed
};

class HomographyProcessor {
public:
    [[nodiscard]] static std::expected<Matrix3x3, EstimationError> estimateDLT(
        std::span<const Point2D> src,
        std::span<const Point2D> dst) noexcept
    {
        if (src.size() != dst.size() || src.size() < 4) {
            return std::unexpected(EstimationError::InsufficientPoints);
        }

        const size_t n = src.size();
        const auto T_src = computeHartleyTransform(src);
        const auto T_dst = computeHartleyTransform(dst);

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

        Matrix3x3 H_norm{};
        H_norm.at(0, 0) = V[0][min_col]; H_norm.at(0, 1) = V[1][min_col]; H_norm.at(0, 2) = V[2][min_col];
        H_norm.at(1, 0) = V[3][min_col]; H_norm.at(1, 1) = V[4][min_col]; H_norm.at(1, 2) = V[5][min_col];
        H_norm.at(2, 0) = V[6][min_col]; H_norm.at(2, 1) = V[7][min_col]; H_norm.at(2, 2) = V[8][min_col];

        const auto inv_T_dst_opt = T_dst.inverse();
        if (!inv_T_dst_opt) return std::unexpected(EstimationError::InversionFailed);

        Matrix3x3 H = (*inv_T_dst_opt) * H_norm * T_src;

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

    [[nodiscard]] static std::expected<EstimationResult, EstimationError> estimateRANSAC(
        std::span<const Point2D> src,
        std::span<const Point2D> dst,
        const RansacConfig& config = {}) noexcept
    {
        if (src.size() != dst.size() || src.size() < 4) {
            return std::unexpected(EstimationError::InsufficientPoints);
        }

        const size_t n = src.size();
        const double thresh_sq = config.max_reprojection_error * config.max_reprojection_error;

        std::mt19937 rng(1337);
        std::uniform_int_distribution<size_t> dist(0, n - 1);

        size_t best_inliers = 0;
        Matrix3x3 best_H{};
        size_t required_iters = config.max_iterations;

        for (size_t iter = 0; iter < required_iters; ++iter) {
            std::array<size_t, 4> indices{};
            for (size_t i = 0; i < 4; ++i) {
                bool unique = false;
                while (!unique) {
                    indices[i] = dist(rng);
                    unique = true;
                    for (size_t j = 0; j < i; ++j) {
                        if (indices[i] == indices[j]) { unique = false; break; }
                    }
                }
            }

            const std::array<Point2D, 4> sample_src = { src[indices[0]], src[indices[1]], src[indices[2]], src[indices[3]] };
            const std::array<Point2D, 4> sample_dst = { dst[indices[0]], dst[indices[1]], dst[indices[2]], dst[indices[3]] };

            auto H_res = estimateDLT(sample_src, sample_dst);
            if (!H_res) continue;

            const auto H_cand = *H_res;
            const auto inv_H_opt = H_cand.inverse();
            if (!inv_H_opt) continue;
            const auto inv_H = *inv_H_opt;

            size_t current_inliers = 0;
            for (size_t i = 0; i < n; ++i) {
                auto p_dst = H_cand.transform(src[i]);
                auto p_src = inv_H.transform(dst[i]);
                if (!p_dst || !p_src) continue;

                const double dx1 = dst[i].x - p_dst->x;
                const double dy1 = dst[i].y - p_dst->y;
                const double dx2 = src[i].x - p_src->x;
                const double dy2 = src[i].y - p_src->y;

                const double sym_err = (dx1 * dx1 + dy1 * dy1) + (dx2 * dx2 + dy2 * dy2);
                if (sym_err < thresh_sq) {
                    current_inliers++;
                }
            }

            if (current_inliers > best_inliers) {
                best_inliers = current_inliers;
                best_H = H_cand;

                const double w = static_cast<double>(current_inliers) / static_cast<double>(n);
                const double w4 = w * w * w * w;
                if (w4 > 1e-6) {
                    const double num = std::log(1.0 - config.confidence);
                    const double den = std::log(1.0 - w4);
                    const auto k = static_cast<size_t>(num / den) + 1;
                    if (k < required_iters) required_iters = k;
                }
            }
        }

        if (best_inliers < 4) {
            return std::unexpected(EstimationError::NoConsensusFound);
        }

        const auto inv_best_H_opt = best_H.inverse();
        if (!inv_best_H_opt) return std::unexpected(EstimationError::InversionFailed);
        const auto inv_best_H = *inv_best_H_opt;

        std::vector<Point2D> final_src, final_dst;
        final_src.reserve(n);
        final_dst.reserve(n);
        std::vector<bool> inlier_mask(n, false);
        double total_err = 0.0;

        for (size_t i = 0; i < n; ++i) {
            auto p_dst = best_H.transform(src[i]);
            auto p_src = inv_best_H.transform(dst[i]);
            if (!p_dst || !p_src) continue;

            const double dx1 = dst[i].x - p_dst->x;
            const double dy1 = dst[i].y - p_dst->y;
            const double dx2 = src[i].x - p_src->x;
            const double dy2 = src[i].y - p_src->y;
            const double sym_err = (dx1 * dx1 + dy1 * dy1) + (dx2 * dx2 + dy2 * dy2);

            if (sym_err < thresh_sq) {
                inlier_mask[i] = true;
                final_src.push_back(src[i]);
                final_dst.push_back(dst[i]);
                total_err += std::sqrt(sym_err * 0.5);
            }
        }

        auto final_H_res = estimateDLT(final_src, final_dst);
        if (!final_H_res) return std::unexpected(final_H_res.error());

        return EstimationResult{
            .H = *final_H_res,
            .inlier_count = final_src.size(),
            .inlier_mask = std::move(inlier_mask),
            .mean_reprojection_error = total_err / static_cast<double>(final_src.size())
        };
    }

    static void warpPerspectiveBilinear(
        std::span<const uint8_t> src_image, size_t src_w, size_t src_h,
        std::span<uint8_t> dst_image, size_t dst_w, size_t dst_h,
        const Matrix3x3& H_dst_to_src) noexcept
    {
        for (size_t dst_y = 0; dst_y < dst_h; ++dst_y) {
            for (size_t dst_x = 0; dst_x < dst_w; ++dst_x) {
                const auto pt_src_opt = H_dst_to_src.transform(Point2D{
                    static_cast<double>(dst_x), static_cast<double>(dst_y)
                });

                const size_t dst_idx = dst_y * dst_w + dst_x;

                if (!pt_src_opt ||
                    pt_src_opt->x < 0.0 || pt_src_opt->x >= static_cast<double>(src_w - 1) ||
                    pt_src_opt->y < 0.0 || pt_src_opt->y >= static_cast<double>(src_h - 1)) {
                    dst_image[dst_idx] = 0;
                    continue;
                }

                const auto& pt = *pt_src_opt;
                const auto x0 = static_cast<size_t>(std::floor(pt.x));
                const auto y0 = static_cast<size_t>(std::floor(pt.y));
                const size_t x1 = x0 + 1;
                const size_t y1 = y0 + 1;

                const double wx1 = pt.x - static_cast<double>(x0);
                const double wy1 = pt.y - static_cast<double>(y0);
                const double wx0 = 1.0 - wx1;
                const double wy0 = 1.0 - wy1;

                const uint8_t p00 = src_image[y0 * src_w + x0];
                const uint8_t p01 = src_image[y0 * src_w + x1];
                const uint8_t p10 = src_image[y1 * src_w + x0];
                const uint8_t p11 = src_image[y1 * src_w + x1];

                const double val = wx0 * wy0 * p00 +
                                   wx1 * wy0 * p01 +
                                   wx0 * wy1 * p10 +
                                   wx1 * wy1 * p11;

                dst_image[dst_idx] = static_cast<uint8_t>(std::clamp(val + 0.5, 0.0, 255.0));
            }
        }
    }

private:
    [[nodiscard]] static Matrix3x3 computeHartleyTransform(std::span<const Point2D> pts) noexcept {
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

        Matrix3x3 T{};
        T.at(0, 0) = scale; T.at(0, 2) = -scale * mean_x;
        T.at(1, 1) = scale; T.at(1, 2) = -scale * mean_y;
        T.at(2, 2) = 1.0;
        return T;
    }

    [[nodiscard]] static std::array<std::array<double, 9>, 9> solveJacobiEigensystem(
        std::array<std::array<double, 9>, 9> A) noexcept
    {
        std::array<std::array<double, 9>, 9> V{};
        for (size_t i = 0; i < 9; ++i) V[i][i] = 1.0;

        constexpr size_t max_iter = 60;
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

} // namespace vision::geometry
