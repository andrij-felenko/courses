#include <vector>
#include <memory>
#include <span>

namespace tsp {

class Solver {
public:
    explicit Solver(Algorithm alg = Algorithm::Christofides) 
        : config_{.algorithm = alg} {}

    Solver& set_metric(MetricType metric) {
        config_.metric = metric;
        return *this;
    }

    Solver& set_time_limit(std::chrono::duration<double> limit) {
        config_.time_limit = limit;
        return *this;
    }

    Solver& set_threads(size_t threads) {
        config_.num_threads = threads;
        return *this;
    }

    [[nodiscard]] Result solve(std::span<const double> matrix_flat, size_t n) const;
    [[nodiscard]] Result solve(const std::vector<std::vector<double>>& matrix) const;
    [[nodiscard]] static bool validate_triangle_inequality(const std::vector<std::vector<double>>& matrix);

private:
    Config config_;
};

} // namespace tsp
