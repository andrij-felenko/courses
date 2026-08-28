/**
 * @file Units.hpp
 * @brief Типобезпечні фізичні величини у системі SI з підтримкою користувацьких літералів C++20.
 */

#pragma once

#include <compare>
#include <cstdint>

namespace sf::devices::units {

/**
 * @brief Типобезпечна обгортка для тиску в Паскалях (Па).
 */
class Pascals {
public:
    constexpr explicit Pascals(float value = 0.0f) noexcept : value_(value) {}

    [[nodiscard]] constexpr float value() const noexcept { return value_; }
    [[nodiscard]] constexpr float hectopascals() const noexcept { return value_ / 100.0f; }
    [[nodiscard]] constexpr float millibars() const noexcept { return value_ / 100.0f; }

    constexpr auto operator<=>(const Pascals&) const noexcept = default;

    constexpr Pascals operator+(Pascals other) const noexcept { return Pascals(value_ + other.value_); }
    constexpr Pascals operator-(Pascals other) const noexcept { return Pascals(value_ - other.value_); }
    constexpr Pascals operator*(float scalar) const noexcept { return Pascals(value_ * scalar); }
    constexpr Pascals operator/(float scalar) const noexcept { return Pascals(value_ / scalar); }

private:
    float value_;
};

/**
 * @brief Типобезпечна обгортка для температури в градусах Цельсія (°C).
 */
class Celsius {
public:
    constexpr explicit Celsius(float value = 0.0f) noexcept : value_(value) {}

    [[nodiscard]] constexpr float value() const noexcept { return value_; }
    [[nodiscard]] constexpr float kelvin() const noexcept { return value_ + 273.15f; }

    constexpr auto operator<=>(const Celsius&) const noexcept = default;

    constexpr Celsius operator+(Celsius other) const noexcept { return Celsius(value_ + other.value_); }
    constexpr Celsius operator-(Celsius other) const noexcept { return Celsius(value_ - other.value_); }
    constexpr Celsius operator*(float scalar) const noexcept { return Celsius(value_ * scalar); }
    constexpr Celsius operator/(float scalar) const noexcept { return Celsius(value_ / scalar); }

private:
    float value_;
};

namespace literals {
    constexpr Pascals operator""_Pa(long double val) noexcept {
        return Pascals(static_cast<float>(val));
    }

    constexpr Pascals operator""_Pa(unsigned long long val) noexcept {
        return Pascals(static_cast<float>(val));
    }

    constexpr Pascals operator""_hPa(long double val) noexcept {
        return Pascals(static_cast<float>(val) * 100.0f);
    }

    constexpr Celsius operator""_C(long double val) noexcept {
        return Celsius(static_cast<float>(val));
    }

    constexpr Celsius operator""_C(unsigned long long val) noexcept {
        return Celsius(static_cast<float>(val));
    }
} // namespace literals

} // namespace sf::devices::units
