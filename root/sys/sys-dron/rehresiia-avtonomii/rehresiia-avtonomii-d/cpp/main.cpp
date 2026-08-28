#include <vector>
#include <span>
#include <cmath>
#include <limits>
#include <algorithm>
#include <memory>
#include <expected>
#include <string_view>

struct Point3D {
    double x{0.0};
    double y{0.0};
    double z{0.0};
    double t{0.0};

    [[nodiscard]] constexpr double distance_to(const Point3D& other) const noexcept {
        const double dx = x - other.x;
        const double dy = y - other.y;
        const double dz = z - other.z;
        return std::sqrt(dx * dx + dy * dy + dz * dz);
    }
};

struct RegressionLimits {
    double max_xte_rms{0.50};     // метри
    double max_xte_peak{1.20};    // метри
    double max_frechet{0.80};     // метри
    double max_dtw_norm{0.40};    // метри/крок
};

struct RegressionReport {
    double xte_rms{0.0};
    double xte_max{0.0};
    double frechet_dist{0.0};
    double dtw_normalized{0.0};
    bool passed{false};
};

class TrajectoryComparator {
public:
    [[nodiscard]] static std::pair<double, double> compute_xte(
        std::span<const Point3D> track,
        const Point3D& seg_a,
        const Point3D& seg_b) noexcept {
        
        if (track.empty()) return {0.0, 0.0};

        const double vx = seg_b.x - seg_a.x;
        const double vy = seg_b.y - seg_a.y;
        const double vz = seg_b.z - seg_a.z;
        const double seg_len_sq = vx * vx + vy * vy + vz * vz;

        double sum_sq_err = 0.0;
        double max_err = 0.0;

        for (const auto& p : track) {
            const double wx = p.x - seg_a.x;
            const double wy = p.y - seg_a.y;
            const double wz = p.z - seg_a.z;

            double t = (seg_len_sq > 1e-9) ? (wx * vx + wy * vy + wz * vz) / seg_len_sq : 0.0;
            t = std::clamp(t, 0.0, 1.0);

            const Point3D proj{seg_a.x + t * vx, seg_a.y + t * vy, seg_a.z + t * vz, p.t};
            const double err = p.distance_to(proj);

            sum_sq_err += err * err;
            max_err = std::max(max_err, err);
        }

        return {std::sqrt(sum_sq_err / static_cast<double>(track.size())), max_err};
    }

    [[nodiscard]] static double compute_frechet(
        std::span<const Point3D> p,
        std::span<const Point3D> q) {
        
        const size_t n = p.size();
        const size_t m = q.size();
        if (n == 0 || m == 0) return std::numeric_limits<double>::infinity();

        std::vector<double> prev_row(m);
        std::vector<double> curr_row(m);

        prev_row[0] = p[0].distance_to(q[0]);
        for (size_t j = 1; j < m; ++j) {
            prev_row[j] = std::max(prev_row[j - 1], p[0].distance_to(q[j]));
        }

        for (size_t i = 1; i < n; ++i) {
            curr_row[0] = std::max(prev_row[0], p[i].distance_to(q[0]));

            for (size_t j = 1; j < m; ++j) {
                const double d = p[i].distance_to(q[j]);
                const double min_prev = std::min({prev_row[j - 1], prev_row[j], curr_row[j - 1]});
                curr_row[j] = std::max(d, min_prev);
            }
            std::swap(prev_row, curr_row);
        }

        return prev_row[m - 1];
    }

    [[nodiscard]] static double compute_dtw(
        std::span<const Point3D> p,
        std::span<const Point3D> q,
        size_t window_r) {
        
        const size_t n = p.size();
        const size_t m = q.size();
        if (n == 0 || m == 0) return std::numeric_limits<double>::infinity();

        constexpr double inf = std::numeric_limits<double>::infinity();
        std::vector<double> matrix(n * m, inf);

        auto at = [&](size_t i, size_t j) -> double& { return matrix[i * m + j]; };

        at(0, 0) = p[0].distance_to(q[0]);

        for (size_t i = 0; i < n; ++i) {
            const size_t j_start = (i > window_r) ? (i - window_r) : 0;
            const size_t j_end = std::min(m, i + window_r + 1);

            for (size_t j = j_start; j < j_end; ++j) {
                if (i == 0 && j == 0) continue;

                const double cost = p[i].distance_to(q[j]);
                double min_prev = inf;

                if (i > 0) min_prev = std::min(min_prev, at(i - 1, j));
                if (j > 0) min_prev = std::min(min_prev, at(i, j - 1));
                if (i > 0 && j > 0) min_prev = std::min(min_prev, at(i - 1, j - 1));

                if (min_prev < inf) {
                    at(i, j) = cost + min_prev;
                }
            }
        }

        const double total_cost = at(n - 1, m - 1);
        return (total_cost < inf) ? (total_cost / static_cast<double>(n + m)) : inf;
    }

    [[nodiscard]] static RegressionReport evaluate(
        std::span<const Point3D> test_track,
        std::span<const Point3D> golden_track,
        const Point3D& seg_a,
        const Point3D& seg_b,
        const RegressionLimits& limits,
        size_t dtw_window = 50) {
        
        const auto [rms, max_err] = compute_xte(test_track, seg_a, seg_b);
        const double frechet = compute_frechet(test_track, golden_track);
        const double dtw = compute_dtw(test_track, golden_track, dtw_window);

        const bool pass = (rms <= limits.max_xte_rms) &&
                          (max_err <= limits.max_xte_peak) &&
                          (frechet <= limits.max_frechet) &&
                          (dtw <= limits.max_dtw_norm);

        return {
            .xte_rms = rms,
            .xte_max = max_err,
            .frechet_dist = frechet,
            .dtw_normalized = dtw,
            .passed = pass
        };
    }
};
