#include <array>
#include <bit>
#include <cstdint>
#include <optional>

constexpr int weight(uint32_t x) noexcept {
    return std::popcount(x);
}

/* Синдром s = B·x ⊕ y. Для симетричної B  B·x = x·B. */
constexpr uint16_t syndrome(uint32_t r) noexcept {
    uint16_t x = r & 0x0FFF;
    uint16_t y = (r >> 12) & 0x0FFF;
    return times_B(x) ^ y;
}

/* Патерн помилки (24 біти) — std::nullopt, якщо помилок 4+. */
constexpr std::optional<uint32_t> golay_error(uint32_t r) noexcept {
    uint16_t s = syndrome(r);
    if (weight(s) <= 3) return (static_cast<uint32_t>(s) << 12);
    for (size_t i = 0; i < 12; ++i) {
        uint16_t t = s ^ B[i];
        if (weight(t) <= 2) return (1u << i) | (static_cast<uint32_t>(t) << 12);
    }
    uint16_t s2 = times_B(s);                 /* B·s, бо B² = I */
    if (weight(s2) <= 3) return static_cast<uint32_t>(s2);
    for (size_t i = 0; i < 12; ++i) {
        uint16_t t = s2 ^ B[i];
        if (weight(t) <= 2) return (static_cast<uint32_t>(1u << i) << 12) | t;
    }
    return std::nullopt;                       /* невиправно: 4+ помилки */
}

/* Виправлені 12 бітів даних — std::nullopt, якщо слово невиправне. */
constexpr std::optional<uint16_t> golay_decode(uint32_t r) noexcept {
    auto err = golay_error(r);
    if (!err) return std::nullopt;
    return static_cast<uint16_t>((r ^ *err) & 0x0FFF);
}
