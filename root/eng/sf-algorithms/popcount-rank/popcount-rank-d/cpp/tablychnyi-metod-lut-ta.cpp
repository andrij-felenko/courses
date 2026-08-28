#include <cstdint>
#include <array>

namespace {
constexpr auto make_popcount_lut() {
    std::array<uint8_t, 256> lut{};
    for (size_t i = 0; i < 256; ++i) {
        uint8_t c = 0;
        for (size_t b = 0; b < 8; ++b) {
            c += static_cast<uint8_t>((i >> b) & 1U);
        }
        lut[i] = c;
    }
    return lut;
}
constexpr auto POPCOUNT_TABLE_256 = make_popcount_lut();
}

[[nodiscard]] constexpr int popcount_lut(uint64_t x) noexcept {
    return POPCOUNT_TABLE_256[x & 0xFF] +
           POPCOUNT_TABLE_256[(x >> 8) & 0xFF] +
           POPCOUNT_TABLE_256[(x >> 16) & 0xFF] +
           POPCOUNT_TABLE_256[(x >> 24) & 0xFF] +
           POPCOUNT_TABLE_256[(x >> 32) & 0xFF] +
           POPCOUNT_TABLE_256[(x >> 40) & 0xFF] +
           POPCOUNT_TABLE_256[(x >> 48) & 0xFF] +
           POPCOUNT_TABLE_256[(x >> 56) & 0xFF];
}
