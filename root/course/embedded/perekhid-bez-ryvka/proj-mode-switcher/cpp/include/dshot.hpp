#pragma once

#include <cstdint>

namespace fc::dshot {

// 11-бітне значення тяги: 0 — команда «стоп», робочий діапазон 48..2047.
[[nodiscard]] constexpr std::uint16_t throttle_value(float unit, bool armed) noexcept
{
    if (!armed || !(unit > 0.0f)) return 0;   // NaN потрапляє сюди — і це правильно
    if (unit > 1.0f) unit = 1.0f;
    return static_cast<std::uint16_t>(48.0f + unit * (2047.0f - 48.0f) + 0.5f);
}

// Кадр: 11 біт значення, біт запиту телеметрії, CRC4 по цих дванадцяти.
[[nodiscard]] constexpr std::uint16_t packet(std::uint16_t value, bool telemetry) noexcept
{
    const auto payload = static_cast<std::uint16_t>(((value & 0x7FFu) << 1) |
                                                    (telemetry ? 1u : 0u));
    const auto crc = static_cast<std::uint16_t>(
        (payload ^ (payload >> 4) ^ (payload >> 8)) & 0x0Fu);
    return static_cast<std::uint16_t>((payload << 4) | crc);
}

}  // namespace fc::dshot
