namespace crypto::pairing {

class BlsSignatureScheme {
public:
    using SignatureBuffer = std::array<std::uint8_t, 48>;
    using PublicKeyBuffer = std::array<std::uint8_t, 96>;
    using SecretKeyBuffer = std::array<std::uint8_t, 32>;

    [[nodiscard]] static std::expected<SignatureBuffer, ErrorCode> sign(
        std::span<const std::uint8_t, 32> secret_key,
        std::span<const std::uint8_t> msg
    ) noexcept;

    [[nodiscard]] static bool verify(
        std::span<const std::uint8_t, 48> signature,
        std::span<const std::uint8_t, 96> public_key,
        std::span<const std::uint8_t> msg
    ) noexcept;
};

} // namespace crypto::pairing
