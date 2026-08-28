#include <cstdint>
#include <optional>
#include <bit>

namespace pairing {

struct Point2D {
    uint32_t x{0};
    uint32_t y{0};
    constexpr bool operator==(const Point2D&) const noexcept = default;
};

/* C++20 constexpr цілочисельний квадратний корінь */
[[nodiscard]] constexpr uint64_t isqrt64(uint64_t n) noexcept {
    if (n == 0) return 0;
    uint64_t root = 0;
    const int lz = std::countl_zero(n);
    const int shift = (63 - lz) & ~1;
    uint64_t bit = static_cast<uint64_t>(1) << shift;

    while (bit != 0) {
        if (n >= root + bit) {
            n -= root + bit;
            root = (root >> 1) + bit;
        } else {
            root >>= 1;
        }
        bit >>= 2;
    }
    return root;
}

/* Безпечне кодування C++20 з поверненням std::optional */
[[nodiscard]] constexpr std::optional<uint64_t> cantor_encode(uint32_t x, uint32_t y) noexcept {
    const uint64_t ux = x;
    const uint64_t uy = y;
    const uint64_t w = ux + uy;

    constexpr uint64_t MAX_W = 6074000999ULL;
    if (w > MAX_W) return std::nullopt;

    return (w * (w + 1)) / 2 + uy;
}

/* Аналітичне розпакування у строго типізовану структуру Point2D */
[[nodiscard]] constexpr std::optional<Point2D> cantor_decode(uint64_t code) noexcept {
    if (code >= (UINT64_MAX / 8)) return std::nullopt;

    const uint64_t s = isqrt64(8 * code + 1);
    const uint64_t w = (s - 1) / 2;
    const uint64_t base = (w * (w + 1)) / 2;
    const uint64_t y = code - base;
    const uint64_t x = w - y;

    if (x > UINT32_MAX || y > UINT32_MAX) return std::nullopt;

    return Point2D{static_cast<uint32_t>(x), static_cast<uint32_t>(y)};
}

} // namespace pairing
