namespace physics::nonlinear::api {

struct GpuConfig {
    int device_id{0};
    std::size_t threads_per_block{256};
};

class GpuGridScanner {
public:
    [[nodiscard]] static std::expected<std::vector<double>, ApiErrorCode> scan_gpu(
        const CircleMapConfig& base_config,
        const GpuConfig& gpu_config,
        const GridBounds& bounds) noexcept;
};

} // namespace physics::nonlinear::api
