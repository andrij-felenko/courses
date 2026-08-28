namespace crypto::pairing {

class HashToCurve {
public:
    [[nodiscard]] static std::expected<std::array<std::uint8_t, 48>, ErrorCode> compress_g1(
        const G1Affine& point
    ) noexcept;

    [[nodiscard]] static std::expected<G1Affine, ErrorCode> hash_to_g1(
        std::span<const std::uint8_t> msg,
        std::span<const std::uint8_t> dst
    ) noexcept;
};

} // namespace crypto::pairing
