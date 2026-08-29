#pragma once

#include <cstdint>
#include <span>

namespace boot {

// CRC-32/IEEE, побітово й без таблиці. constexpr не заради краси: та сама
// функція рахує контрольну суму заголовка на льоту й перевіряє себе на
// етапі компіляції у static_assert нижче.
[[nodiscard]] constexpr std::uint32_t crc32(std::span<const std::uint8_t> data) noexcept
{
    std::uint32_t crc = 0xFFFFFFFFU;

    for (const std::uint8_t byte : data) {
        crc ^= byte;
        for (int bit = 0; bit < 8; ++bit) {
            const std::uint32_t mask = (crc & 1U) != 0U ? 0xEDB88320U : 0U;
            crc = (crc >> 1) ^ mask;
        }
    }

    return ~crc;
}

namespace detail {
inline constexpr std::uint8_t kCrcProbe[] = {'1', '2', '3', '4', '5',
                                             '6', '7', '8', '9'};
} // namespace detail

// Класичний контрольний вектор CRC-32: "123456789" → 0xCBF43926.
static_assert(crc32(detail::kCrcProbe) == 0xCBF43926U,
              "CRC-32 не збігається з еталонним вектором");

} // namespace boot
