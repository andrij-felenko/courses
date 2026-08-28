namespace physics::nonlinear::api {

struct GoldenRatioMetrics {
    double golden_w{0.618033988749895};
    double critical_k{1.0};
    double lyapunov{0.0};
};

class GoldenRatioAnalyzer {
public:
    [[nodiscard]] static std::expected<GoldenRatioMetrics, ApiErrorCode> analyze(
        std::size_t steps = 100000) noexcept;
};

} // namespace physics::nonlinear::api
