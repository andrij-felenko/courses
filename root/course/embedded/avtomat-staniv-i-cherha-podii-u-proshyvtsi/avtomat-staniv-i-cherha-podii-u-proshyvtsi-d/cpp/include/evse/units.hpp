#pragma once

#include <chrono>
#include <compare>
#include <cstdint>

namespace evse {

using Millis = std::chrono::milliseconds;
using Micros = std::chrono::microseconds;

/*
 * Величина з одиницею виміру. Обгортка коштує нуль байтів і нуль тактів, але
 * робить неможливим сплутати мілівольти з міліамперами — типова помилка в
 * прошивці, де все зводиться до uint16_t.
 */
template <class Tag, class Rep>
class Quantity {
public:
    using rep = Rep;

    constexpr Quantity() noexcept = default;
    constexpr explicit Quantity(Rep value) noexcept : value_{value} {}

    [[nodiscard]] constexpr Rep count() const noexcept { return value_; }

    constexpr auto operator<=>(const Quantity&) const noexcept = default;
    constexpr bool operator==(const Quantity&) const noexcept = default;

private:
    Rep value_{};
};

using Millivolts = Quantity<struct MillivoltsTag, std::int16_t>;
using Milliamps  = Quantity<struct MilliampsTag, std::uint16_t>;
using Amperes    = Quantity<struct AmperesTag, std::uint16_t>;

inline namespace literals {

constexpr Millivolts operator""_mV(unsigned long long v) noexcept
{
    return Millivolts{static_cast<std::int16_t>(v)};
}

constexpr Milliamps operator""_mA(unsigned long long v) noexcept
{
    return Milliamps{static_cast<std::uint16_t>(v)};
}

constexpr Amperes operator""_A(unsigned long long v) noexcept
{
    return Amperes{static_cast<std::uint16_t>(v)};
}

} // namespace literals

/*
 * Шпаруватість лінії Control Pilot. Конструктор закритий, тому неможливо
 * випадково подати 200 % або переплутати відсотки з амперами: значення
 * народжується лише в одній із трьох іменованих фабрик.
 */
class Duty {
public:
    constexpr Duty() noexcept = default;

    /* Постійні +12 В: ШІМ вимкнено, станція нічого не пропонує. */
    [[nodiscard]] static constexpr Duty steadyHigh() noexcept { return Duty{100}; }

    [[nodiscard]] static constexpr Duty fromPercent(std::uint8_t p) noexcept
    {
        return Duty{p > 100 ? std::uint8_t{100} : p};
    }

    /*
     * Стандарт J1772: для 6…51 А дозволений струм дорівнює шпаруватості,
     * помноженій на 0,6 А. Отже шпаруватість = I / 0,6.
     */
    [[nodiscard]] static constexpr Duty fromCurrent(Amperes current) noexcept
    {
        const auto amps = current.count();
        if (amps < 6) {
            return Duty{0}; /* заряджання заборонено */
        }
        const auto clamped = amps > 51 ? std::uint16_t{51} : amps;
        return Duty{static_cast<std::uint8_t>((clamped * 10 + 3) / 6)};
    }

    [[nodiscard]] constexpr std::uint8_t percent() const noexcept { return percent_; }

    /* На 100 % генератор ШІМ вимкнено, і періоду в лінії немає. */
    [[nodiscard]] constexpr bool pwmActive() const noexcept
    {
        return percent_ > 0 && percent_ < 100;
    }

    constexpr bool operator==(const Duty&) const noexcept = default;

private:
    constexpr explicit Duty(std::uint8_t p) noexcept : percent_{p} {}

    std::uint8_t percent_{100};
};

} // namespace evse
