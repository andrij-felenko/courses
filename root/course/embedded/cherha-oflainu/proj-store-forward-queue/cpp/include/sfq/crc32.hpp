// crc32.hpp — CRC-32 за IEEE 802.3 (поліном 0xEDB88320 у відображеній формі).
//
// Таблицю не набираємо руками: її будує consteval-функція під час
// компіляції. Магічних шістнадцяткових стовпчиків у коді немає, а в
// прошивку лягають ті самі 64 байти констант.
#pragma once

#include <array>
#include <concepts>
#include <cstddef>
#include <cstdint>
#include <span>

namespace sfq {

inline constexpr std::uint32_t kCrcSeed = 0xFFFFFFFFu;

namespace detail {

consteval std::array<std::uint32_t, 16> make_nibble_table() noexcept
{
    std::array<std::uint32_t, 16> table{};
    for (std::uint32_t i = 0; i < table.size(); ++i) {
        std::uint32_t value = i;
        for (int bit = 0; bit < 4; ++bit) {
            value = (value & 1u) ? (0xEDB88320u ^ (value >> 1)) : (value >> 1);
        }
        table[i] = value;
    }
    return table;
}

inline constexpr auto kNibbleTable = make_nibble_table();

}  // namespace detail

// Потокова форма: суму можна накопичувати по шматках.
[[nodiscard]] constexpr std::uint32_t crc32_update(std::uint32_t crc,
                                                   std::span<const std::byte> data) noexcept
{
    for (const std::byte b : data) {
        crc ^= std::to_integer<std::uint8_t>(b);
        crc = (crc >> 4) ^ detail::kNibbleTable[crc & 0x0Fu];
        crc = (crc >> 4) ^ detail::kNibbleTable[crc & 0x0Fu];
    }
    return crc;
}

[[nodiscard]] constexpr std::uint32_t crc32_finish(std::uint32_t crc) noexcept
{
    return crc ^ 0xFFFFFFFFu;
}

[[nodiscard]] constexpr std::uint32_t crc32(std::span<const std::byte> data) noexcept
{
    return crc32_finish(crc32_update(kCrcSeed, data));
}

}  // namespace sfq
