#pragma once

#include <compare>
#include <cstdint>
#include <expected>
#include <limits>

// Арифметика з фіксованою комою: ціле число з домовленою вагою розряду.
namespace fx {

enum class ArithError { division_by_zero };

// Звуження 64→32 біти з обмеженням по краях (те, що на Cortex-M робить SSAT).
[[nodiscard]] constexpr std::int32_t saturate(std::int64_t v) noexcept {
    constexpr std::int64_t hi = std::numeric_limits<std::int32_t>::max();
    constexpr std::int64_t lo = std::numeric_limits<std::int32_t>::min();
    return static_cast<std::int32_t>(v > hi ? hi : (v < lo ? lo : v));
}

// Обмеження знакового числа розрядністю Bits: аналог SSAT Rd, #Bits, Rn.
template <int Bits>
[[nodiscard]] constexpr std::int32_t saturate_bits(std::int32_t v) noexcept {
    static_assert(Bits > 1 && Bits <= 32);
    if constexpr (Bits == 32) {
        return v;
    } else {
        constexpr std::int32_t hi = (std::int32_t{1} << (Bits - 1)) - 1;
        constexpr std::int32_t lo = -(std::int32_t{1} << (Bits - 1));
        return v > hi ? hi : (v < lo ? lo : v);
    }
}

template <int Frac = 16>
class Fixed {
    static_assert(Frac > 0 && Frac < 31, "дробова частина мусить лишити місце цілій");

public:
    static constexpr int frac_bits = Frac;
    static constexpr std::int64_t one = std::int64_t{1} << Frac;
    static constexpr std::int64_t half_lsb = std::int64_t{1} << (Frac - 1);

    constexpr Fixed() noexcept = default;

    [[nodiscard]] static constexpr Fixed from_raw(std::int32_t r) noexcept {
        Fixed f;
        f.raw_ = r;
        return f;
    }

    // consteval: дійсне число дозволене ЛИШЕ на етапі трансляції.
    // У прошивку йде готова ціла константа, підпрограми IEEE 754 не тягнуться.
    [[nodiscard]] static consteval Fixed from_real(long double v) noexcept {
        const long double scaled = v * static_cast<long double>(one);
        return from_raw(static_cast<std::int32_t>(scaled + (v < 0 ? -0.5L : 0.5L)));
    }

    [[nodiscard]] static constexpr Fixed from_int(std::int32_t v) noexcept {
        return from_raw(saturate(static_cast<std::int64_t>(v) * one));
    }

    [[nodiscard]] constexpr std::int32_t raw() const noexcept { return raw_; }

    // Симетричне округлення: зсув праворуч округлює донизу, тож для
    // від'ємних додаємо половину ваги LSB зі знаком мінус.
    [[nodiscard]] constexpr std::int32_t to_int() const noexcept {
        const std::int64_t bias = raw_ >= 0 ? half_lsb : -half_lsb;
        return static_cast<std::int32_t>((static_cast<std::int64_t>(raw_) + bias) >> Frac);
    }

    [[nodiscard]] friend constexpr Fixed operator+(Fixed a, Fixed b) noexcept {
        return from_raw(saturate(static_cast<std::int64_t>(a.raw_) + b.raw_));
    }

    [[nodiscard]] friend constexpr Fixed operator-(Fixed a, Fixed b) noexcept {
        return from_raw(saturate(static_cast<std::int64_t>(a.raw_) - b.raw_));
    }

    // Q_n * Q_n дає Q_2n; повертаємось до Q_n зсувом проміжного 64-бітного
    // добутку (на ARM це SMULL і зсув регістрової пари).
    [[nodiscard]] friend constexpr Fixed operator*(Fixed a, Fixed b) noexcept {
        const std::int64_t prod = static_cast<std::int64_t>(a.raw_) * b.raw_;
        const std::int64_t bias = prod >= 0 ? half_lsb : -half_lsb;
        return from_raw(saturate((prod + bias) >> Frac));
    }

    // Ділення може не мати відповіді — про це каже тип, а не -1 та errno.
    [[nodiscard]] constexpr std::expected<Fixed, ArithError> divide(Fixed d) const noexcept {
        if (d.raw_ == 0) {
            return std::unexpected(ArithError::division_by_zero);
        }
        std::int64_t num = static_cast<std::int64_t>(raw_) << Frac;
        const std::int64_t half = (d.raw_ >= 0 ? d.raw_ : -static_cast<std::int64_t>(d.raw_)) / 2;
        num += num >= 0 ? half : -half;
        return from_raw(saturate(num / d.raw_));
    }

    [[nodiscard]] friend constexpr auto operator<=>(Fixed, Fixed) noexcept = default;

private:
    std::int32_t raw_{0};
};

using Q16 = Fixed<16>;

// Множення сирого відліку на вагу молодшого розряду: на вході ціле, на
// виході ціле фізичних одиниць, проміжок — 64 біти.
template <int Frac>
[[nodiscard]] constexpr std::int32_t scale_raw(std::int32_t centred, Fixed<Frac> weight) noexcept {
    const std::int64_t prod = static_cast<std::int64_t>(centred) * weight.raw();
    const std::int64_t bias = prod >= 0 ? Fixed<Frac>::half_lsb : -Fixed<Frac>::half_lsb;
    return saturate((prod + bias) >> Frac);
}

// Ціла частина кореня: модуль вектора без FPU.
[[nodiscard]] constexpr std::uint32_t isqrt(std::uint64_t v) noexcept {
    if (v == 0) {
        return 0;
    }
    std::uint64_t x = v;
    std::uint64_t y = 1;
    while (x > y) {
        x = (x + y) / 2;
        y = v / x;
    }
    return static_cast<std::uint32_t>(x);
}

} // namespace fx
