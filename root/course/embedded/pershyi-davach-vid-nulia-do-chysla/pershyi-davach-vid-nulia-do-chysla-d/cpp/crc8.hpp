#pragma once

/* CRC-8 у варіанті Sensirion: поліном 0x31, init 0xFF, без відображень.
   Функція constexpr, тож правильність перевіряється ще на компіляції. */

#include <array>
#include <cstdint>
#include <span>

namespace sht3x {

inline constexpr std::uint8_t kCrcPolynomial = 0x31;
inline constexpr std::uint8_t kCrcInit       = 0xFF;

[[nodiscard]] constexpr std::uint8_t crc8(std::span<const std::uint8_t> data) noexcept
{
    std::uint8_t crc = kCrcInit;

    for (const std::uint8_t byte : data) {
        crc ^= byte;
        for (int bit = 0; bit < 8; ++bit) {
            // Виліт старшого розряду з регістра означає XOR із поліномом.
            crc = (crc & 0x80) != 0
                      ? static_cast<std::uint8_t>((crc << 1) ^ kCrcPolynomial)
                      : static_cast<std::uint8_t>(crc << 1);
        }
    }
    return crc;
}

namespace detail {
// Перевірочне слово з даташиту: 0xBE 0xEF мусить дати 0x92.
inline constexpr std::array<std::uint8_t, 2> kCheckWord{0xBE, 0xEF};
}  // namespace detail

static_assert(crc8(detail::kCheckWord) == 0x92,
              "CRC-8 розійшовся з перевірочним словом даташиту");

}  // namespace sht3x
