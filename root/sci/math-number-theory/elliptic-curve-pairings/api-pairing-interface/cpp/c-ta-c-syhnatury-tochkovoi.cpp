namespace crypto::pairing {

class G1Group {
public:
    [[nodiscard]] static G1Affine generator() noexcept;

    [[nodiscard]] static std::expected<G1Affine, ErrorCode> scalar_mul(
        const G1Affine& point,
        std::span<const std::uint8_t, 32> scalar
    ) noexcept;

    [[nodiscard]] static bool is_in_correct_subgroup(const G1Affine& point) noexcept;
};

} // namespace crypto::pairing
