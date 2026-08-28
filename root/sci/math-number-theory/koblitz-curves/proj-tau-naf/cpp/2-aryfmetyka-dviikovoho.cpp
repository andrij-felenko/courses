#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <vector>
#include <utility>

namespace koblitz {

inline constexpr size_t FieldWords = 4;
inline constexpr size_t MaxTnafLen = 240;

struct FieldElement {
    std::array<uint64_t, FieldWords> words{};

    [[nodiscard]] constexpr bool is_zero() const noexcept {
        return words[0] == 0 && words[1] == 0 && words[2] == 0 && words[3] == 0;
    }
};

/* Таблиця розширення байтів для піднесення до квадрата в характеристиці 2 */
inline constexpr std::array<uint16_t, 256> generate_sqr_table() noexcept {
    std::array<uint16_t, 256> tbl{};
    for (size_t i = 0; i < 256; ++i) {
        uint16_t val = 0;
        for (size_t b = 0; b < 8; ++b) {
            if ((i >> b) & 1) {
                val |= static_cast<uint16_t>(1 << (2 * b));
            }
        }
        tbl[i] = val;
    }
    return tbl;
}

inline constexpr auto SqrTable = generate_sqr_table();

[[nodiscard]] constexpr uint64_t sqr_word(uint32_t w) noexcept {
    return (static_cast<uint64_t>(SqrTable[(w >> 24) & 0xFF]) << 48) |
           (static_cast<uint64_t>(SqrTable[(w >> 16) & 0xFF]) << 32) |
           (static_cast<uint64_t>(SqrTable[(w >> 8) & 0xFF]) << 16) |
           (static_cast<uint64_t>(SqrTable[w & 0xFF]));
}

/* Піднесення до квадрата в полі F_{2^233} з редукцією за f(x) = x^233 + x^74 + 1 */
[[nodiscard]] FieldElement square(const FieldElement& a) noexcept {
    std::array<uint64_t, 8> wide{};
    for (size_t i = 0; i < FieldWords; ++i) {
        wide[2 * i]     = sqr_word(static_cast<uint32_t>(a.words[i] & 0xFFFFFFFF));
        wide[2 * i + 1] = sqr_word(static_cast<uint32_t>(a.words[i] >> 32));
    }

    for (size_t i = 7; i >= 4; --i) {
        const uint64_t top = wide[i];
        if (top == 0) continue;

        wide[i - 4] ^= (top >> 41);
        wide[i - 3] ^= (top << 23) ^ (top >> 25);
        wide[i - 2] ^= (top << 39);
        wide[i] = 0;
    }

    const uint64_t top_rem = wide[3] >> 41;
    wide[3] &= 0x1FFFFFFFFFFULL;
    wide[0] ^= top_rem;
    wide[1] ^= (top_rem << 74) | (top_rem >> 54);

    return FieldElement{ .words = { wide[0], wide[1], wide[2], wide[3] } };
}

} // namespace koblitz
