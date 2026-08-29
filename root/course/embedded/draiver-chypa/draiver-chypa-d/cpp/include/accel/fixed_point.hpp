// fixed_point.hpp — перетворення без плаваючої коми.
//
// На Cortex-M0/M0+/M3 апаратного FPU немає: кожна операція над float — виклик
// бібліотечної функції. Цілий шлях дає мілігравітації та міліметри на секунду
// в квадраті, а проміжні добутки завжди рахуються в 64 бітах.
#pragma once

#include <cstdint>
#include <span>

#include "types.hpp"

namespace accel::fixed {

// 1 мкg = 9.80665e-6 м/с² = 9.80665 мкм/с².
inline constexpr std::int64_t kMicroGToMicroMetreNum = 980665;
inline constexpr std::int64_t kMicroGToMicroMetreDen = 100000;

[[nodiscard]] constexpr std::int32_t divideRounded(std::int64_t numerator,
                                                   std::int64_t denominator) noexcept
{
    if (denominator == 0) {
        return 0;
    }
    const std::int64_t half = denominator / 2;
    const std::int64_t result = (numerator >= 0) ? (numerator + half) / denominator
                                                 : (numerator - half) / denominator;
    return static_cast<std::int32_t>(result);
}

[[nodiscard]] constexpr std::int32_t toMilliG(std::int16_t raw, Range range) noexcept
{
    const auto microG = static_cast<std::int64_t>(raw) * sensitivityMicroG(range);
    return divideRounded(microG, 1000);
}

[[nodiscard]] constexpr std::int32_t toMillimetrePerSecond2(std::int16_t raw, Range range) noexcept
{
    const auto microG = static_cast<std::int64_t>(raw) * sensitivityMicroG(range);
    return divideRounded(microG * kMicroGToMicroMetreNum, kMicroGToMicroMetreDen * 1000);
}

// Порядок байтів little-endian: молодший іде першим.
[[nodiscard]] constexpr std::uint16_t littleEndian(std::span<const std::uint8_t, 2> pair) noexcept
{
    return static_cast<std::uint16_t>(pair[0] | (static_cast<std::uint16_t>(pair[1]) << 8));
}

// Розширення знака з урахуванням роздільності. Для 12-бітного відліку,
// вирівняного по лівому краю, слово зсувається вправо на чотири позиції, а
// знак добудовується явно: покладатися на арифметичний зсув знакового типу
// переносний код не має права.
[[nodiscard]] constexpr std::int16_t signExtend(std::uint16_t word, Resolution resolution) noexcept
{
    const auto shift = static_cast<unsigned>(resolution);
    const unsigned bits = 16U - shift;

    const auto magnitudeMask = static_cast<std::uint32_t>((1UL << bits) - 1UL);
    const auto signBit = static_cast<std::uint32_t>(1UL << (bits - 1U));

    const std::uint32_t value = (static_cast<std::uint32_t>(word) >> shift) & magnitudeMask;
    return static_cast<std::int16_t>(static_cast<std::int32_t>(value ^ signBit) -
                                     static_cast<std::int32_t>(signBit));
}

} // namespace accel::fixed
