namespace pairing {

/**
 * @brief Верифіковане C++ кодування пари координат.
 * @pre (uint64_t)x + (uint64_t)y <= 6074000999ULL
 * @post return.has_value() ==> cantor_decode(*return) == Pair32{x, y}
 */
[[nodiscard]] constexpr std::optional<uint64_t> cantor_encode_verified(uint32_t x, uint32_t y) noexcept {
    const uint64_t ux = x;
    const uint64_t uy = y;
    const uint64_t w = ux + uy;
    if (w > 6074000999ULL) return std::nullopt;
    return (w * (w + 1)) / 2 + uy;
}

} // namespace pairing
