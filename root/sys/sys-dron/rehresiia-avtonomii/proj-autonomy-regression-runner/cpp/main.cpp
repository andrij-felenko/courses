#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <span>
#include <string>
#include <string_view>
#include <cmath>
#include <limits>
#include <algorithm>
#include <memory>
#include <expected>
#include <filesystem>

struct FlightPoint {
    double t{0.0};
    double x{0.0};
    double y{0.0};
    double z{0.0};
    double vx{0.0};
    double vy{0.0};
    double vz{0.0};
    double voltage{0.0};
    double current{0.0};

    [[nodiscard]] constexpr double distance_to(const FlightPoint& other) const noexcept {
        const double dx = x - other.x;
        const double dy = y - other.y;
        const double dz = z - other.z;
        return std::sqrt(dx * dx + dy * dy + dz * dz);
    }
};

struct RegressionLimits {
    double max_frechet{0.80};
    double max_dtw_norm{0.35};
    double max_xte_rms{0.40};
    double max_xte_peak{1.00};
    double max_energy_pct{5.0};
    size_t dtw_window{60};
};

struct RegressionResults {
    double frechet_distance{0.0};
    double dtw_normalized{0.0};
    double energy_test_joules{0.0};
    double energy_golden_joules{0.0};
    double energy_delta_pct{0.0};
    bool passed{false};
};

class TelemetryLoader {
public:
    [[nodiscard]] static std::expected<std::vector<FlightPoint>, std::string> load_csv(const std::filesystem::path& path) {
        std::ifstream file(path);
        if (!file.is_open()) {
            return std::unexpected("Cannot open file: " + path.string());
        }

        std::vector<FlightPoint> points;
        points.reserve(4096);

        std::string line;
        if (!std::getline(file, line)) {
            return std::unexpected("Empty CSV file: " + path.string());
        }

        while (std::getline(file, line)) {
            if (line.empty()) continue;
            std::stringstream ss(line);
            std::string token;
            std::vector<std::string> cols;

            while (std::getline(ss, token, ',')) {
                cols.push_back(token);
            }

            if (cols.size() >= 12) {
                try {
                    FlightPoint pt{
                        .t = std::stoull(cols[0]) * 1e-6,
                        .x = std::stod(cols[1]),
                        .y = std::stod(cols[2]),
                        .z = std::stod(cols[3]),
                        .vx = std::stod(cols[4]),
                        .vy = std::stod(cols[5]),
                        .vz = std::stod(cols[6]),
                        .voltage = std::stod(cols[10]),
                        .current = std::stod(cols[11])
                    };
                    points.push_back(pt);
                } catch (...) {
                    continue;
                }
            }
        }

        if (points.empty()) {
            return std::unexpected("No valid telemetry points parsed from: " + path.string());
        }

        return points;
    }
};

class AutonomyRegressionEngine {
public:
    [[nodiscard]] static double compute_frechet(std::span<const FlightPoint> p, std::span<const FlightPoint> q) {
        const size_t n = p.size();
        const size_t m = q.size();
        if (n == 0 || m == 0) return std::numeric_limits<double>::infinity();

        std::vector<double> prev(m);
        std::vector<double> curr(m);

        prev[0] = p[0].distance_to(q[0]);
        for (size_t j = 1; j < m; ++j) {
            prev[j] = std::max(prev[j - 1], p[0].distance_to(q[j]));
        }

        for (size_t i = 1; i < n; ++i) {
            curr[0] = std::max(prev[0], p[i].distance_to(q[0]));

            for (size_t j = 1; j < m; ++j) {
                const double d = p[i].distance_to(q[j]);
                const double min_prev = std::min({prev[j - 1], prev[j], curr[j - 1]});
                curr[j] = std::max(d, min_prev);
            }
            std::swap(prev, curr);
        }

        return prev[m - 1];
    }

    [[nodiscard]] static double compute_dtw(std::span<const FlightPoint> p, std::span<const FlightPoint> q, size_t r) {
        const size_t n = p.size();
        const size_t m = q.size();
        if (n == 0 || m == 0) return std::numeric_limits<double>::infinity();

        constexpr double inf = std::numeric_limits<double>::infinity();
        std::vector<double> matrix(n * m, inf);

        auto at = [&](size_t i, size_t j) -> double& { return matrix[i * m + j]; };

        at(0, 0) = p[0].distance_to(q[0]);

        for (size_t i = 0; i < n; ++i) {
            const size_t j_start = (i > r) ? (i - r) : 0;
            const size_t j_end = std::min(m, i + r + 1);

            for (size_t j = j_start; j < j_end; ++j) {
                if (i == 0 && j == 0) continue;
                const double cost = p[i].distance_to(q[j]);
                double min_prev = inf;

                if (i > 0) min_prev = std::min(min_prev, at(i - 1, j));
                if (j > 0) min_prev = std::min(min_prev, at(i, j - 1));
                if (i > 0 && j > 0) min_prev = std::min(min_prev, at(i - 1, j - 1));

                if (min_prev < inf) at(i, j) = cost + min_prev;
            }
        }

        const double total = at(n - 1, m - 1);
        return (total < inf) ? (total / static_cast<double>(n + m)) : inf;
    }

    [[nodiscard]] static double compute_energy(std::span<const FlightPoint> traj) noexcept {
        double energy_joules{0.0};
        for (size_t i = 0; i + 1 < traj.size(); ++i) {
            const double dt = traj[i + 1].t - traj[i].t;
            if (dt > 0.0 && dt < 1.0) {
                const double p1 = traj[i].voltage * traj[i].current;
                const double p2 = traj[i + 1].voltage * traj[i + 1].current;
                energy_joules += 0.5 * (p1 + p2) * dt;
            }
        }
        return energy_joules;
    }

    [[nodiscard]] static RegressionResults evaluate(
        std::span<const FlightPoint> test_traj,
        std::span<const FlightPoint> golden_traj,
        const RegressionLimits& limits) {
        
        const double frechet = compute_frechet(test_traj, golden_traj);
        const double dtw = compute_dtw(test_traj, golden_traj, limits.dtw_window);
        const double e_test = compute_energy(test_traj);
        const double e_gold = compute_energy(golden_traj);
        const double e_delta = (e_gold > 0.0) ? ((e_test - e_gold) / e_gold * 100.0) : 0.0;

        const bool pass = (frechet <= limits.max_frechet) &&
                          (dtw <= limits.max_dtw_norm) &&
                          (e_delta <= limits.max_energy_pct);

        return {
            .frechet_distance = frechet,
            .dtw_normalized = dtw,
            .energy_test_joules = e_test,
            .energy_golden_joules = e_gold,
            .energy_delta_pct = e_delta,
            .passed = pass
        };
    }
};

int main(int argc, char** argv) {
    std::string test_path, golden_path, json_out = "regression_summary.json", junit_out = "junit.xml";
    RegressionLimits limits;

    for (int i = 1; i < argc; ++i) {
        std::string_view arg{argv[i]};
        if (arg == "--test" && i + 1 < argc) test_path = argv[++i];
        else if (arg == "--golden" && i + 1 < argc) golden_path = argv[++i];
        else if (arg == "--max-frechet" && i + 1 < argc) limits.max_frechet = std::stod(argv[++i]);
        else if (arg == "--max-dtw" && i + 1 < argc) limits.max_dtw_norm = std::stod(argv[++i]);
        else if (arg == "--dtw-window" && i + 1 < argc) limits.dtw_window = std::stoul(argv[++i]);
        else if (arg == "--json-out" && i + 1 < argc) json_out = argv[++i];
        else if (arg == "--junit-out" && i + 1 < argc) junit_out = argv[++i];
    }

    if (test_path.empty() || golden_path.empty()) {
        std::cerr << "Usage: " << argv[0] << " --test <test.csv> --golden <golden.csv> [options]\n";
        return 2;
    }

    const auto test_points = TelemetryLoader::load_csv(test_path);
    const auto golden_points = TelemetryLoader::load_csv(golden_path);

    if (!test_points || !golden_points) {
        std::cerr << "Error loading telemetry files.\n";
        return 2;
    }

    const auto results = AutonomyRegressionEngine::evaluate(*test_points, *golden_points, limits);

    std::cout << "=== AUTONOMY REGRESSION REPORT (C++20) ===\n";
    std::cout << "Frechet Distance: " << results.frechet_distance << " m (Limit: <= " << limits.max_frechet << ")\n";
    std::cout << "DTW Normalized:   " << results.dtw_normalized << " m/step (Limit: <= " << limits.max_dtw_norm << ")\n";
    std::cout << "Energy Delta:     " << results.energy_delta_pct << " % (Limit: <= " << limits.max_energy_pct << ")\n";
    std::cout << "Final Status:     " << (results.passed ? "PASS" : "FAIL") << "\n";

    return results.passed ? 0 : 1;
}
