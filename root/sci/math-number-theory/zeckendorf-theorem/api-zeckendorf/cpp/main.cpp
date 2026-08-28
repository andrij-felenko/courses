namespace math::zeckendorf {

struct ZeckendorfResult {
    std::vector<bool> bits;
    uint64_t value;
};

class EncoderDecoder {
public:
    explicit EncoderDecoder(size_t max_precomputed_terms = 90);

    [[nodiscard]] std::vector<bool> encode(uint64_t n) const;
    [[nodiscard]] std::expected<uint64_t, ErrorCode> decode(std::span<const bool> bits) const noexcept;
    
    [[nodiscard]] std::vector<uint8_t> pack_to_fibstream(uint64_t n) const;
    [[nodiscard]] std::expected<uint64_t, ErrorCode> unpack_from_fibstream(std::span<const uint8_t> bytes) const;
};

} // namespace math::zeckendorf
