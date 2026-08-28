namespace physics::nonlinear::api {

class MpiGridScanner {
public:
    [[nodiscard]] static std::expected<std::vector<double>, ApiErrorCode> scan_distributed(
        const CircleMapConfig& base_config,
        const GridBounds& bounds) noexcept;
};

} // namespace physics::nonlinear::api
