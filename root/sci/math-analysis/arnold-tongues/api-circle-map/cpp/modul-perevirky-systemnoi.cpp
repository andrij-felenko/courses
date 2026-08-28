namespace physics::nonlinear::api {

struct SystemCapabilities {
    bool has_avx2{false};
    bool has_fp16{false};
    std::size_t simd_width{4};
};

class CapabilityInspector {
public:
    [[nodiscard]] static SystemCapabilities inspect() noexcept;
};

} // namespace physics::nonlinear::api
