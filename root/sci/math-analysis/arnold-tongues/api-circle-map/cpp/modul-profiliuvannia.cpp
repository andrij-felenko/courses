namespace physics::nonlinear::api {

struct PerformanceMetrics {
    double execution_time_seconds{0.0};
    double iterations_per_second{0.0};
    std::size_t cache_misses_est{0};
};

class Profiler {
public:
    [[nodiscard]] static PerformanceMetrics benchmark_solver(
        const CircleMapConfig& config) noexcept;
};

} // namespace physics::nonlinear::api
