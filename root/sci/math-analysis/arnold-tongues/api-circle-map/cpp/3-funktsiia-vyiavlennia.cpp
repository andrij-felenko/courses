namespace physics::nonlinear::api {

struct TongueBoundaries {
    double omega_left{0.0};
    double omega_right{0.0};
    double width{0.0};
};

class TongueBoundaryFinder {
public:
    [[nodiscard]] static std::expected<TongueBoundaries, ApiErrorCode> find_boundaries(
        double k_val, int p, int q, double tolerance = 1e-6) noexcept;
};

} // namespace physics::nonlinear::api
