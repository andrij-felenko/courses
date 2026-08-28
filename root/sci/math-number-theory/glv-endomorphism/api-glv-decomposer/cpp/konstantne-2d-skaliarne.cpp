namespace crypto::glv {

[[nodiscard]] Status mul_2d(
    std::span<uint64_t, 12> res_point,
    std::span<const uint64_t, 12> point,
    std::span<const uint64_t, 4> scalar,
    const CurveConfig2D& config
) noexcept;

} // namespace crypto::glv
