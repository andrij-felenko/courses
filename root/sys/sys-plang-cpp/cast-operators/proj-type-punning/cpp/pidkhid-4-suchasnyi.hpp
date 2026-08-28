#include <bit>
#include <cstdint>

// Повністю безпечно, zero-cost, працює в constexpr під час компіляції!
constexpr bool is_negative_bit_cast(float f) noexcept {
    const auto u = std::bit_cast<uint32_t>(f);
    return (u & 0x80000000u) != 0;
}

// Перевірка під час компіляції:
static_assert(is_negative_bit_cast(-1.0f) == true);
static_assert(is_negative_bit_cast(1.0f) == false);
