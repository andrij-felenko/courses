#include <cstdint>
#include <cstddef>
#include <cstring>
#include <span>
#include <string_view>

namespace demo_hash {

constexpr std::uint64_t C1 = 0x87c37b91114253d5ULL;
constexpr std::uint64_t C2 = 0x4cf5ad432745937fULL;

[[nodiscard]] inline std::uint64_t load64(const std::uint8_t* p) noexcept {
    std::uint64_t v;
    std::memcpy(&v, p, sizeof(v));
    return v;
}

[[nodiscard]] constexpr std::uint64_t rotl64(std::uint64_t x, std::int8_t r) noexcept {
    return (x << r) | (x >> (64 - r));
}

[[nodiscard]] std::uint64_t simple_fast_hash(std::span<const std::uint8_t> data, std::uint64_t seed = 0) noexcept {
    const std::size_t len = data.size();
    const std::size_t nblocks = len / 8;
    const std::uint8_t* ptr = data.data();
    std::uint64_t h1 = seed ^ (len * C1);

    for (std::size_t i = 0; i < nblocks; ++i) {
        std::uint64_t k1 = load64(ptr + i * 8);
        k1 *= C1;
        k1 = rotl64(k1, 31);
        k1 *= C2;

        h1 ^= k1;
        h1 = rotl64(h1, 27);
        h1 = h1 * 5 + 0x52dce729;
    }

    h1 ^= len;
    h1 ^= h1 >> 33;
    h1 *= 0xff51afd7565a1a5dULL;
    h1 ^= h1 >> 33;
    return h1;
}

} // namespace demo_hash
