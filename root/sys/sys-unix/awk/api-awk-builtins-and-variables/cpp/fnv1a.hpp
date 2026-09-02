// fnv1a.hpp — FNV-1a на 64 біти: constexpr, без алокацій, над string_view.
// На відміну від C-версії тут не потрібні ні окремий .cpp, ні буфер від
// викликача: хеш і його шістнадцятковий запис обчислюються в чистих
// функціях, а за потреби — ще на етапі компіляції.
#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <string_view>

namespace fast_tools {

inline constexpr std::uint64_t kOffsetBasis = 14695981039346656037ULL;
inline constexpr std::uint64_t kPrime       = 1099511628211ULL;

// "0x" + 16 цифр; термінального нуля масив не містить — довжину віддаємо явно.
inline constexpr std::size_t kHexLength = 18;

[[nodiscard]] constexpr std::uint64_t fnv1a_64(std::string_view data) noexcept
{
    std::uint64_t hash = kOffsetBasis;
    for (const char c : data) {
        // Саме uint8_t: char на багатьох платформах знаковий, і байт 0x80
        // без цього приведення розповз би одиницями по всіх старших бітах.
        hash ^= static_cast<std::uint8_t>(c);
        hash *= kPrime;
    }
    return hash;
}

[[nodiscard]] constexpr std::array<char, kHexLength> to_hex(std::uint64_t value) noexcept
{
    constexpr std::string_view digits = "0123456789abcdef";

    std::array<char, kHexLength> out{};
    out[0] = '0';
    out[1] = 'x';
    for (std::size_t i = 0; i < 16; ++i) {
        const unsigned shift = static_cast<unsigned>(4 * (15 - i));
        out[2 + i] = digits[(value >> shift) & 0xFu];
    }
    return out;
}

// Той самий хеш, але поданий у вигляді, зручному для секціонування: номер
// партиції з [0, buckets). Модуль береться від УСІХ 64 бітів — молодші біти
// FNV-1a розподілені гірше за старші, і зріз лише по них дає перекіс.
[[nodiscard]] constexpr std::uint64_t partition_of(std::string_view data,
                                                   std::uint64_t buckets) noexcept
{
    return buckets == 0 ? 0 : fnv1a_64(data) % buckets;
}

static_assert(fnv1a_64("") == kOffsetBasis,
              "порожній вхід мусить давати базис, а не нуль");
static_assert(to_hex(0)[2] == '0' && to_hex(0)[17] == '0',
              "нуль друкується шістнадцятьма нулями");

} // namespace fast_tools
