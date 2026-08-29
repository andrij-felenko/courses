#pragma once

#include <algorithm>
#include <array>
#include <cstdint>
#include <numeric>
#include <span>

#include "crc8.hpp"

namespace errscan {

// Кадр — два байти даних плюс байт захисту.
inline constexpr int frame_bits = 24;

struct stats {
    unsigned long checked = 0;     // скільки спотворень перебрано
    unsigned long missed_crc = 0;  // скільки пройшло повз CRC-8
    unsigned long missed_sum = 0;  // скільки пройшло повз арифметичну суму
};

// Арифметична контрольна сума: додавання байтів за модулем 256.
[[nodiscard]] constexpr std::uint8_t checksum(std::span<const std::uint8_t> data) noexcept
{
    return static_cast<std::uint8_t>(
        std::accumulate(data.begin(), data.end(), 0u) & 0xFFu);
}

namespace detail {

// Один кадр під двома кодами: спотворення накладаються на обидва синхронно.
struct guarded {
    std::array<std::uint8_t, 3> crc{};
    std::array<std::uint8_t, 3> sum{};

    constexpr void flip(int bit) noexcept
    {
        const auto mask = static_cast<std::uint8_t>(0x80u >> (bit % 8));
        crc[static_cast<std::size_t>(bit / 8)] ^= mask;
        sum[static_cast<std::size_t>(bit / 8)] ^= mask;
    }

    [[nodiscard]] constexpr bool crc_passes() const noexcept
    {
        return crc8::of(std::span<const std::uint8_t>{crc}.first(2)) == crc[2];
    }

    [[nodiscard]] constexpr bool sum_passes() const noexcept
    {
        return checksum(std::span<const std::uint8_t>{sum}.first(2)) == sum[2];
    }
};

[[nodiscard]] constexpr guarded build(std::uint16_t word) noexcept
{
    guarded g{};
    g.crc[0] = g.sum[0] = static_cast<std::uint8_t>(word >> 8);
    g.crc[1] = g.sum[1] = static_cast<std::uint8_t>(word);
    g.crc[2] = crc8::of(std::span<const std::uint8_t>{g.crc}.first(2));
    g.sum[2] = checksum(std::span<const std::uint8_t>{g.sum}.first(2));
    return g;
}

constexpr void judge(const guarded& g, stats& st) noexcept
{
    ++st.checked;
    if (g.crc_passes()) {
        ++st.missed_crc; // приймач узяв би зіпсований кадр за справжній
    }
    if (g.sum_passes()) {
        ++st.missed_sum;
    }
}

constexpr void walk(guarded& g, int start, int left, stats& st) noexcept
{
    if (left == 0) {
        judge(g, st);
        return;
    }
    for (int b = start; b <= frame_bits - left; ++b) {
        g.flip(b);
        walk(g, b + 1, left - 1, st);
        g.flip(b); // повертаємо біт на місце
    }
}

// Інверсія (або її скасування) для одного пакетного спотворення.
constexpr void toggle_burst(guarded& g, int start, int len, unsigned inner) noexcept
{
    g.flip(start);
    if (len >= 2) {
        g.flip(start + len - 1);
        for (int k = 0; k < len - 2; ++k) {
            if (inner & (1u << k)) {
                g.flip(start + 1 + k);
            }
        }
    }
}

} // namespace detail

// Усі комбінації рівно bits інвертованих бітів кадру.
[[nodiscard]] constexpr stats flips(std::uint16_t word, int bits) noexcept
{
    stats st{};
    if (bits < 1 || bits > frame_bits) {
        return st;
    }
    auto g = detail::build(word);
    detail::walk(g, 0, bits, st);
    return st;
}

// Пакетні помилки довжиною 1..max_len: крайні біти вікна спотворені завжди,
// внутрішні — у всіх можливих поєднаннях.
[[nodiscard]] constexpr stats bursts(std::uint16_t word, int max_len) noexcept
{
    stats st{};
    if (max_len < 1) {
        return st;
    }
    max_len = std::min(max_len, frame_bits);
    auto g = detail::build(word);
    for (int len = 1; len <= max_len; ++len) {
        const unsigned variants = (len >= 2) ? (1u << (len - 2)) : 1u;
        for (int start = 0; start + len <= frame_bits; ++start) {
            for (unsigned inner = 0; inner < variants; ++inner) {
                detail::toggle_burst(g, start, len, inner);
                detail::judge(g, st);
                detail::toggle_burst(g, start, len, inner);
            }
        }
    }
    return st;
}

// Обіцянка статті: одиночні помилки й пакети до восьми бітів не проходять.
static_assert(flips(0xBEEF, 1).missed_crc == 0);
static_assert(bursts(0xBEEF, 8).missed_crc == 0);

} // namespace errscan
