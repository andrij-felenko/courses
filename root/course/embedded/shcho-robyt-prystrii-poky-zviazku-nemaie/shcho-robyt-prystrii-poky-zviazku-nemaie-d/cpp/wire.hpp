#pragma once

#include <bit>
#include <cstddef>
#include <cstdint>
#include <span>

// Дріт і Flash бачать байти, а не структури. Тут — рівно те, що потрібно
// обом користувачам: порядок little-endian, CRC-16/CCITT і мітка автентичності.
namespace cart::wire {

inline void putU16(std::span<std::byte> b, std::size_t at, std::uint16_t v) noexcept {
    b[at + 0] = static_cast<std::byte>(v & 0xFFU);
    b[at + 1] = static_cast<std::byte>((v >> 8) & 0xFFU);
}

inline void putU32(std::span<std::byte> b, std::size_t at, std::uint32_t v) noexcept {
    for (std::size_t i = 0; i < 4; ++i) b[at + i] = static_cast<std::byte>((v >> (8 * i)) & 0xFFU);
}

inline void putI16(std::span<std::byte> b, std::size_t at, std::int16_t v) noexcept {
    putU16(b, at, static_cast<std::uint16_t>(v));
}

inline void putF32(std::span<std::byte> b, std::size_t at, float v) noexcept {
    putU32(b, at, std::bit_cast<std::uint32_t>(v));
}

[[nodiscard]] inline std::uint16_t u16(std::span<const std::byte> b, std::size_t at) noexcept {
    return static_cast<std::uint16_t>(std::to_integer<std::uint16_t>(b[at]) |
                                      (std::to_integer<std::uint16_t>(b[at + 1]) << 8));
}

[[nodiscard]] inline std::uint32_t u32(std::span<const std::byte> b, std::size_t at) noexcept {
    std::uint32_t v = 0;
    for (std::size_t i = 0; i < 4; ++i) v |= std::to_integer<std::uint32_t>(b[at + i]) << (8 * i);
    return v;
}

[[nodiscard]] inline std::int16_t i16(std::span<const std::byte> b, std::size_t at) noexcept {
    return static_cast<std::int16_t>(u16(b, at));
}

[[nodiscard]] inline float f32(std::span<const std::byte> b, std::size_t at) noexcept {
    return std::bit_cast<float>(u32(b, at));
}

[[nodiscard]] inline std::uint16_t crc16(std::span<const std::byte> data) noexcept {
    std::uint16_t crc = 0xFFFFU;
    for (std::byte raw : data) {
        crc ^= static_cast<std::uint16_t>(std::to_integer<std::uint16_t>(raw) << 8);
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x8000U) ? static_cast<std::uint16_t>((crc << 1) ^ 0x1021U)
                                  : static_cast<std::uint16_t>(crc << 1);
        }
    }
    return crc;
}

// У виробі тут AES-CMAC або Poly1305 із ключем у захищеній пам'яті; для
// заняття беремо keyed FNV-1a. Важливе не саме перетворення, а те, ЩО ця
// перевірка стоїть перед годуванням мертвої руки.
[[nodiscard]] inline std::uint32_t authTag(std::span<const std::byte> data, std::uint32_t key) noexcept {
    std::uint32_t h = 2166136261u ^ key;
    for (std::byte raw : data) {
        h ^= std::to_integer<std::uint32_t>(raw);
        h *= 16777619u;
    }
    h ^= key;
    h *= 16777619u;
    return h;
}

}  // namespace cart::wire
