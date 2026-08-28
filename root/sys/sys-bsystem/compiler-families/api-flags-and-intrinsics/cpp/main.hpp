#include <cstdint>
#include <bit>

// Починаючи з C++20 стандартна бібліотека <bit> повністю
// абстрагує апаратні інтринсики процесора для всіх компіляторів.
constexpr std::uint32_t count_leading_zeros32(std::uint32_t x) noexcept {
    return static_cast<std::uint32_t>(std::countl_zero(x));
}

constexpr std::uint32_t popcount32(std::uint32_t x) noexcept {
    return static_cast<std::uint32_t>(std::popcount(x));
}
