#pragma once

#include <cstdint>
#include <span>

namespace radio {

// CRC-16/CCITT-FALSE: x^16 + x^12 + x^5 + 1, Init = 0xFFFF, без фінального XOR.
// Усе constexpr — та сама функція годиться і для перевірки на етапі компіляції.
inline constexpr std::uint16_t kCrcPoly = 0x1021;
inline constexpr std::uint16_t kCrcInit = 0xFFFF;

[[nodiscard]] constexpr std::uint16_t crcUpdate(std::uint16_t crc, std::uint8_t byte) noexcept
{
    // Байт лягає у старшу половину регістра: далі вісім зсувів, і на кожному,
    // де виїхала одиниця, домішуємо поліном.
    crc ^= static_cast<std::uint16_t>(static_cast<std::uint16_t>(byte) << 8);

    for (int i = 0; i < 8; ++i) {
        const bool msb = (crc & 0x8000u) != 0;
        crc = static_cast<std::uint16_t>(crc << 1);
        if (msb) {
            crc = static_cast<std::uint16_t>(crc ^ kCrcPoly);
        }
    }
    return crc;
}

[[nodiscard]] constexpr std::uint16_t crc16(std::span<const std::uint8_t> data) noexcept
{
    std::uint16_t crc = kCrcInit;
    for (const std::uint8_t byte : data) {
        crc = crcUpdate(crc, byte);
    }
    return crc;
}

} // namespace radio
