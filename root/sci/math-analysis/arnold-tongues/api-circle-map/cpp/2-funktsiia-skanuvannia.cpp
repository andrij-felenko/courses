namespace physics::nonlinear::api {

struct GridBounds {
    double omega_min{0.0};
    double omega_max{1.0};
    std::size_t res_omega{100};
    double k_min{0.0};
    double k_max{1.0};
    std::size_t res_k{100};
};

class GridScanner {
public:
    explicit GridScanner(CircleMapConfig base_config)
        : base_config_{base_config} {}

    [[nodiscard]] std::expected<std::vector<SimulationResult>, ApiErrorCode> scan(
        const GridBounds& bounds) const;

private:
    CircleMapConfig base_config_;
};

} // namespace physics::nonlinear::api
