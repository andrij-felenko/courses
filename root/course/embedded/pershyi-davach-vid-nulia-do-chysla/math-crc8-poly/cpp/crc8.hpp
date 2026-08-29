#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>

namespace crc8 {

// G(x) = x^8 + x^5 + x^4 + 1 без старшого біта x^8.
inline constexpr std::uint8_t poly = 0x31;
// Початковий стан регістра для SHT3x/SHT4x.
inline constexpr std::uint8_t init = 0xFF;

// Один такт зсувного регістра: віднімання полінома в GF(2) — це XOR.
[[nodiscard]] constexpr std::uint8_t shift(std::uint8_t reg) noexcept
{
    return (reg & 0x80) ? static_cast<std::uint8_t>((reg << 1) ^ poly)
                        : static_cast<std::uint8_t>(reg << 1);
}

// Побітовий автомат: вісім тактів на кожен байт.
[[nodiscard]] constexpr std::uint8_t bitwise(std::span<const std::uint8_t> data) noexcept
{
    std::uint8_t reg = init;
    for (const std::uint8_t byte : data) {
        reg ^= byte;
        for (int b = 0; b < 8; ++b) {
            reg = shift(reg);
        }
    }
    return reg;
}

// Таблиця будується компілятором і лягає в незмінну пам'ять готовою.
[[nodiscard]] constexpr std::array<std::uint8_t, 256> make_table() noexcept
{
    std::array<std::uint8_t, 256> table{};
    for (std::size_t i = 0; i < table.size(); ++i) {
        std::uint8_t reg = static_cast<std::uint8_t>(i);
        for (int b = 0; b < 8; ++b) {
            reg = shift(reg);
        }
        table[i] = reg;
    }
    return table;
}

inline constexpr auto table = make_table();

// Табличний розрахунок: XOR і читання на байт.
[[nodiscard]] constexpr std::uint8_t of(std::span<const std::uint8_t> data) noexcept
{
    std::uint8_t reg = init;
    for (const std::uint8_t byte : data) {
        reg = table[static_cast<std::uint8_t>(reg ^ byte)];
    }
    return reg;
}

// Проміжні стани регістра за вісім тактів одного байта.
[[nodiscard]] constexpr std::array<std::uint8_t, 8> trace(std::uint8_t reg,
                                                          std::uint8_t data) noexcept
{
    std::array<std::uint8_t, 8> steps{};
    reg ^= data;
    for (int b = 0; b < 8; ++b) {
        reg = shift(reg);
        steps[static_cast<std::size_t>(b)] = reg;
    }
    return steps;
}

// Прогін кадру разом із його байтом CRC дає нульовий залишок.
[[nodiscard]] constexpr bool frame_ok(std::span<const std::uint8_t> frame) noexcept
{
    return frame.size() >= 2 && of(frame) == 0x00;
}

enum class frame_error {
    short_frame,
    crc_mismatch,
};

// Кадр SHT3x: старший байт, молодший байт, CRC. Замість -1 та errno — expected.
[[nodiscard]] constexpr std::expected<std::uint16_t, frame_error>
word(std::span<const std::uint8_t> frame) noexcept
{
    if (frame.size() != 3) {
        return std::unexpected(frame_error::short_frame);
    }
    if (of(frame.first(2)) != frame[2]) {
        return std::unexpected(frame_error::crc_mismatch);
    }
    return static_cast<std::uint16_t>((frame[0] << 8) | frame[1]);
}

// Контрольні значення перевіряються ще на компіляції.
static_assert(of(std::array<std::uint8_t, 2>{0xBE, 0xEF}) == 0x92);
static_assert(bitwise(std::array<std::uint8_t, 2>{0xBE, 0xEF}) == 0x92);
static_assert(of(std::array<std::uint8_t, 9>{0x31, 0x32, 0x33, 0x34, 0x35,
                                             0x36, 0x37, 0x38, 0x39}) == 0xF7);
static_assert(frame_ok(std::array<std::uint8_t, 3>{0xBE, 0xEF, 0x92}));
static_assert(word(std::array<std::uint8_t, 3>{0xBE, 0xEF, 0x92}) == 0xBEEF);
static_assert(!word(std::array<std::uint8_t, 3>{0xBE, 0xEE, 0x92}).has_value());
static_assert(table[1] == 0x31 && table[2] == 0x62);

} // namespace crc8
