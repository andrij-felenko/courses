namespace crypto::pairing {

class PairingEngine {
public:
    [[nodiscard]] static std::expected<Fp12, ErrorCode> miller_loop(
        const G1Affine& P,
        const G2Affine& Q
    ) noexcept;

    [[nodiscard]] static std::expected<Fp12, ErrorCode> multi_pairing(
        std::span<const G1Affine> P_array,
        std::span<const G2Affine> Q_array
    ) noexcept;
};

} // namespace crypto::pairing
