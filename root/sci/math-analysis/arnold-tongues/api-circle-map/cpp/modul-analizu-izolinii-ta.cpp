namespace physics::nonlinear::api {

struct IsoclineConfig {
    double target_w{0.5};
    double k_start{0.0};
    double k_end{1.0};
    std::size_t steps_k{100};
};

struct IsoclinePoint {
    double omega{0.0};
    double k{0.0};
};

class IsoclineTracer {
public:
    [[nodiscard]] static std::expected<std::vector<IsoclinePoint>, ApiErrorCode> trace(
        const IsoclineConfig& config) noexcept;
};

} // namespace physics::nonlinear::api
