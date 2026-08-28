namespace crypto::pairing {

struct KzgSrs {
    std::span<const G1Affine> g1_powers;
    G2Affine g2_s;
};

class KzgScheme {
public:
    [[nodiscard]] static std::expected<std::array<std::uint8_t, 48>, ErrorCode> commit(
        const KzgSrs& srs,
        std::span<const std::uint8_t> coeffs
    ) noexcept;
};

} // namespace crypto::pairing
