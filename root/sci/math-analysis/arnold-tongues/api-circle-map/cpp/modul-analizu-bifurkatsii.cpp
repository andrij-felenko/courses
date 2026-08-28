namespace physics::nonlinear::api {

struct BifurcationPoint {
    double k_bifurcation{0.0};
    int period{1};
    double feigenbaum_delta{4.6692016};
};

class BifurcationAnalyzer {
public:
    [[nodiscard]] static std::expected<BifurcationPoint, ApiErrorCode> find_next_bifurcation(
        double k_start, int current_period) noexcept;
};

} // namespace physics::nonlinear::api
