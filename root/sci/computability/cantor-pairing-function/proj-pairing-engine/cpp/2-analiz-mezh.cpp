namespace pairing {

struct Pair32 {
    uint32_t x{0};
    uint32_t y{0};

    constexpr bool operator==(const Pair32&) const noexcept = default;
};

struct Pair64 {
    uint64_t x{0};
    uint64_t y{0};

    constexpr bool operator==(const Pair64&) const noexcept = default;
};

/* Безпечне C++20 кодування з поверненням std::optional для контролю помилок */
[[nodiscard]] constexpr std::optional<uint64_t> cantor_encode(uint32_t x, uint32_t y) noexcept {
    const uint64_t ux = x;
    const uint64_t uy = y;
    const uint64_t w = ux + uy;

    constexpr uint64_t MAX_W = 6074000999ULL;
    if (w > MAX_W) {
        return std::nullopt;
    }

    const uint64_t base = (w * (w + 1)) / 2;
    return base + uy;
}

/* Декодування 64-бітного індексу Кантора у строго типізовану структуру Pair32 */
[[nodiscard]] constexpr std::optional<Pair32> cantor_decode(uint64_t code) noexcept {
    if (code >= (UINT64_MAX / 8)) {
        #if defined(__SIZEOF_INT128__)
            unsigned __int128 disc = (static_cast<unsigned __int128>(code) * 8) + 1;
            unsigned __int128 r = 0, b = static_cast<unsigned __int128>(1) << 126;
            while (b > disc) b >>= 2;
            while (b != 0) {
                if (disc >= r + b) {
                    disc -= r + b;
                    r = (r >> 1) + b;
                } else {
                    r >>= 1;
                }
                b >>= 2;
            }
            uint64_t s = static_cast<uint64_t>(r);
            uint64_t w = (s - 1) / 2;
            uint64_t base = (w * (w + 1)) / 2;
            uint64_t y = code - base;
            uint64_t x = w - y;

            if (x > UINT32_MAX || y > UINT32_MAX) return std::nullopt;
            return Pair32{static_cast<uint32_t>(x), static_cast<uint32_t>(y)};
        #else
            return std::nullopt;
        #endif
    }

    const uint64_t s = isqrt64(8 * code + 1);
    const uint64_t w = (s - 1) / 2;
    const uint64_t base = (w * (w + 1)) / 2;
    const uint64_t y = code - base;
    const uint64_t x = w - y;

    if (x > UINT32_MAX || y > UINT32_MAX) {
        return std::nullopt;
    }

    return Pair32{static_cast<uint32_t>(x), static_cast<uint32_t>(y)};
}

} // namespace pairing
