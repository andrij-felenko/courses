#include <vector>
#include <chrono>
#include <functional>

namespace tsp {

using ProgressCallback = std::function<bool(double progress)>;

struct Config {
    Algorithm algorithm{Algorithm::Christofides};
    MetricType metric{MetricType::General};
    std::chrono::duration<double> time_limit{0};
    double target_precision{0.0};
    size_t num_threads{1};
    ProgressCallback callback{nullptr};
};

struct Result {
    Status status{Status::Success};
    double tour_cost{0.0};
    std::vector<size_t> tour;
    std::chrono::duration<double> elapsed_time{0};
    uint64_t nodes_evaluated{0};
};

} // namespace tsp
