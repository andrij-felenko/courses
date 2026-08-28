namespace physics::nonlinear::api {

struct CoupledSystemConfig {
    std::vector<double> omegas;
    double k_global{0.5};
    double coupling_strength{0.1};
    std::size_t steps{10000};
};

class CoupledCircleMapSolver {
public:
    [[nodiscard]] static std::expected<std::vector<double>, ApiErrorCode> solve_ensemble(
        const CoupledSystemConfig& config) noexcept;
};

} // namespace physics::nonlinear::api
