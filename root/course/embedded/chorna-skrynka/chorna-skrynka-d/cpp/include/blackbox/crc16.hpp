// crc16.hpp — CRC-16/CCITT-FALSE (поліном 0x1021, seed 0xFFFF).
//
// constexpr: контрольну суму еталонного кадру можна порахувати ще на етапі
// компіляції й перевірити static_assert-ом, не запускаючи плату.
#pragma once

#include <cstddef>
#include <cstdint>
#include <span>

namespace blackbox {

[[nodiscard]] constexpr std::uint16_t crc16_ccitt(std::span<const std::byte> bytes,
                                                  std::uint16_t seed = 0xFFFFu) noexcept
{
    std::uint16_t crc = seed;
    for (const std::byte b : bytes) {
        crc ^= static_cast<std::uint16_t>(std::to_integer<std::uint8_t>(b) << 8);
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x8000u) ? static_cast<std::uint16_t>((crc << 1) ^ 0x1021u)
                                  : static_cast<std::uint16_t>(crc << 1);
        }
    }
    return crc;
}

} // namespace blackbox
