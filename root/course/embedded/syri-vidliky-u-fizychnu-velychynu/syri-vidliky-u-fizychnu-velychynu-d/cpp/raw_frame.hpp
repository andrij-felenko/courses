#pragma once

#include <cstdint>
#include <expected>
#include <span>

// Складання відліків із буфера пакетного читання. Буфер лишається
// послідовністю байтів: reinterpret_cast на int16_t* — це HardFault на
// ядрі без апаратної підтримки непарного доступу.
namespace raw {

enum class FrameError { short_buffer, bad_width };

// Ширина поля відома на етапі трансляції — перевіряє компілятор.
template <int Bits>
[[nodiscard]] constexpr std::int16_t sign_extend(std::uint16_t v) noexcept {
    static_assert(Bits > 1 && Bits <= 16, "поле від 2 до 16 бітів");
    if constexpr (Bits == 16) {
        return static_cast<std::int16_t>(v);
    } else {
        constexpr auto mask = static_cast<std::uint16_t>(0xFFFFu << Bits);
        constexpr auto sign = static_cast<std::uint16_t>(1u << (Bits - 1));
        auto field = static_cast<std::uint16_t>(v & static_cast<std::uint16_t>(~mask));
        if ((field & sign) != 0) {
            field = static_cast<std::uint16_t>(field | mask);
        }
        // З C++20 перетворення в знаковий тип означене як доповняльний код.
        return static_cast<std::int16_t>(field);
    }
}

[[nodiscard]] constexpr std::uint16_t assemble_le(std::uint8_t lo, std::uint8_t hi) noexcept {
    return static_cast<std::uint16_t>(lo | (static_cast<std::uint16_t>(hi) << 8));
}

[[nodiscard]] constexpr std::uint16_t assemble_be(std::uint8_t hi, std::uint8_t lo) noexcept {
    return static_cast<std::uint16_t>((static_cast<std::uint16_t>(hi) << 8) | lo);
}

// 20-бітний відлік BMP280: три байти старшим уперед, службові молодші чотири.
[[nodiscard]] constexpr std::uint32_t assemble_be20(std::span<const std::uint8_t, 3> b) noexcept {
    const auto w = (static_cast<std::uint32_t>(b[0]) << 16) |
                   (static_cast<std::uint32_t>(b[1]) << 8) | static_cast<std::uint32_t>(b[2]);
    return w >> 4;
}

struct Vec3Raw {
    std::int16_t x{0};
    std::int16_t y{0};
    std::int16_t z{0};
};

// Розкладка значущих бітів усередині 16-бітного кадру.
enum class Layout {
    left_aligned_le,  // значущі в старших розрядах, LSB-first (LIS3DH)
    right_aligned_le, // значущі в молодших розрядах, LSB-first (ADS1115)
    full_be16         // повні 16 бітів, MSB-first (MPU6050)
};

// Ліве вирівнювання: знак уже на місці, лишається арифметичний зсув.
template <int Bits = 12>
[[nodiscard]] constexpr Vec3Raw parse_left_aligned(std::span<const std::uint8_t, 6> b) noexcept {
    constexpr int shift = 16 - Bits;
    auto axis = [](std::uint8_t lo, std::uint8_t hi) constexpr {
        const auto word = static_cast<std::int16_t>(assemble_le(lo, hi));
        return static_cast<std::int16_t>(word >> shift);
    };
    return Vec3Raw{axis(b[0], b[1]), axis(b[2], b[3]), axis(b[4], b[5])};
}

// Праве вирівнювання: без розширення від'ємне число стало б додатним.
template <int Bits = 12>
[[nodiscard]] constexpr Vec3Raw parse_right_aligned(std::span<const std::uint8_t, 6> b) noexcept {
    auto axis = [](std::uint8_t lo, std::uint8_t hi) constexpr {
        return sign_extend<Bits>(assemble_le(lo, hi));
    };
    return Vec3Raw{axis(b[0], b[1]), axis(b[2], b[3]), axis(b[4], b[5])};
}

[[nodiscard]] constexpr Vec3Raw parse_be16(std::span<const std::uint8_t, 6> b) noexcept {
    auto axis = [](std::uint8_t hi, std::uint8_t lo) constexpr {
        return static_cast<std::int16_t>(assemble_be(hi, lo));
    };
    return Vec3Raw{axis(b[0], b[1]), axis(b[2], b[3]), axis(b[4], b[5])};
}

// Вхід із шини має довжину лише в рантаймі: коротку відповідь драйвера
// повертаємо типом, а не кодом -1.
template <int Bits = 12>
[[nodiscard]] constexpr std::expected<Vec3Raw, FrameError> parse(std::span<const std::uint8_t> bytes,
                                                                 Layout layout) noexcept {
    if (bytes.size() < 6) {
        return std::unexpected(FrameError::short_buffer);
    }
    const auto six = bytes.first<6>();
    switch (layout) {
    case Layout::left_aligned_le:
        return parse_left_aligned<Bits>(six);
    case Layout::right_aligned_le:
        return parse_right_aligned<Bits>(six);
    case Layout::full_be16:
        return parse_be16(six);
    }
    return std::unexpected(FrameError::bad_width);
}

} // namespace raw
