class G2Compressor {
public:
    [[nodiscard]] std::expected<void, TwistStatus> compress(
        std::span<std::uint8_t> out_compressed,
        std::span<const std::uint8_t> in_uncompressed
    ) const noexcept;

    [[nodiscard]] std::expected<void, TwistStatus> decompress(
        std::span<std::uint8_t> out_uncompressed,
        std::span<const std::uint8_t> in_compressed
    ) const noexcept;
};
