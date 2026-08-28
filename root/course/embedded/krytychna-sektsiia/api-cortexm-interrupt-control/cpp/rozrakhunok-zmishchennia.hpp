#include <cstdint>

constexpr std::uint32_t kNvicPrioBits = 4U;

[[nodiscard]] constexpr std::uint8_t calc_basepri(std::uint8_t priority) noexcept {
    return static_cast<std::uint8_t>(priority << (8U - kNvicPrioBits));
}

// Пріоритет 5 перетворюється на 0x50 під час компіляції
constexpr std::uint8_t kBasepriThreshold = calc_basepri(5U);
