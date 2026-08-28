#include <cstdint>
#include <cstddef>
#include <cstring>
#include <string_view>
#include <span>
#include <bit>

namespace fast_hash {

constexpr std::uint64_t C1 = 0x87c37b91114253d5ULL;
constexpr std::uint64_t C2 = 0x4cf5ad432745937fULL;
constexpr std::uint64_t FINAL_M1 = 0xff51afd7565a1a5dULL;
constexpr std::uint64_t FINAL_M2 = 0xc4ceb9fe1a85ec53ULL;

[[nodiscard]] constexpr std::uint64_t rotl64(std::uint64_t x, std::int8_t r) noexcept {
    return (x << r) | (x >> (64 - r));
}

[[nodiscard]] inline std::uint64_t load64(const std::uint8_t* p) noexcept {
    std::uint64_t v;
    std::memcpy(&v, p, sizeof(v));
    return v;
}

[[nodiscard]] inline std::uint64_t fmix64(std::uint64_t k) noexcept {
    k ^= k >> 33;
    k *= FINAL_M1;
    k ^= k >> 33;
    k *= FINAL_M2;
    k ^= k >> 33;
    return k;
}

// Ідіоматичний С++20 інтерфейс через std::span
[[nodiscard]] std::uint64_t hash64(std::span<const std::uint8_t> data, std::uint64_t seed = 0) noexcept {
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

    const std::uint8_t* tail = ptr + nblocks * 8;
    std::uint64_t k2 = 0;

    switch (len & 7) {
    case 7: k2 ^= static_cast<std::uint64_t>(tail[6]) << 48; [[fallthrough]];
    case 6: k2 ^= static_cast<std::uint64_t>(tail[5]) << 40; [[fallthrough]];
    case 5: k2 ^= static_cast<std::uint64_t>(tail[4]) << 32; [[fallthrough]];
    case 4: k2 ^= static_cast<std::uint64_t>(tail[3]) << 24; [[fallthrough]];
    case 3: k2 ^= static_cast<std::uint64_t>(tail[2]) << 16; [[fallthrough]];
    case 2: k2 ^= static_cast<std::uint64_t>(tail[1]) << 8;  [[fallthrough]];
    case 1: k2 ^= static_cast<std::uint64_t>(tail[0]);
            k2 *= C1;
            k2 = rotl64(k2, 31);
            k2 *= C2;
            h1 ^= k2;
    }

    h1 ^= len;
    return fmix64(h1);
}

// Перевантаження для роботи із std::string_view
[[nodiscard]] inline std::uint64_t hash64(std::string_view str, std::uint64_t seed = 0) noexcept {
    return hash64(std::span<const std::uint8_t>(reinterpret_cast<const std::uint8_t*>(str.data()), str.size()), seed);
}

} // namespace fast_hash
