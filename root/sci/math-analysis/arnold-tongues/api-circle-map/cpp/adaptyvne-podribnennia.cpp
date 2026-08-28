namespace physics::nonlinear::api {

struct AdaptiveConfig {
    double delta_threshold{1e-3};
    std::size_t max_depth{5};
};

class AdaptiveGridScanner {
public:
    [[nodiscard]] static std::expected<void, ApiErrorCode> scan_adaptive(
        const CircleMapConfig& base_config,
        const AdaptiveConfig& adapt_config,
        const GridBounds& bounds) noexcept;
};

} // namespace physics::nonlinear::api
