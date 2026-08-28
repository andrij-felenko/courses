namespace pairing {

/* Квадратне спарювання Шудзіка (C++20) */
[[nodiscard]] constexpr uint64_t szudzik_encode(uint32_t x, uint32_t y) noexcept {
    const uint64_t ux = x;
    const uint64_t uy = y;
    return (ux < uy) ? (uy * uy + ux) : (ux * ux + ux + uy);
}

[[nodiscard]] constexpr Pair32 szudzik_decode(uint64_t code) noexcept {
    const uint64_t s = isqrt64(code);
    const uint64_t diff = code - (s * s);
    if (diff < s) {
        return Pair32{static_cast<uint32_t>(diff), static_cast<uint32_t>(s)};
    }
    return Pair32{static_cast<uint32_t>(s), static_cast<uint32_t>(diff - s)};
}

/* Кодування Мортона (Z-order) з бітовими масками */
[[nodiscard]] constexpr uint32_t morton2d_encode(uint16_t x, uint16_t y) noexcept {
    auto spread_bits = [](uint16_t v) constexpr -> uint32_t {
        uint32_t r = v;
        r = (r | (r << 8)) & 0x00FF00FF;
        r = (r | (r << 4)) & 0x0F0F0F0F;
        r = (r | (r << 2)) & 0x33333333;
        r = (r | (r << 1)) & 0x55555555;
        return r;
    };

    return spread_bits(x) | (spread_bits(y) << 1);
}

} // namespace pairing
