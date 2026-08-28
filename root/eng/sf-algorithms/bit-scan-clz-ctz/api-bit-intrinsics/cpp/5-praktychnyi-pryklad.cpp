#include <cstdint>
#include <bit>
#include <concepts>

// В C++20 всі операції доступні з коробки без необхідності ручних перевірок
template <std::unsigned_integral T>
[[nodiscard]] constexpr int get_leading_zeros(T val) noexcept {
    return std::countl_zero(val); // Повністю безпечно для 0: повертає розрядність типу
}

template <std::unsigned_integral T>
[[nodiscard]] constexpr int calculate_bit_width(T val) noexcept {
    return std::bit_width(val); // Повертає 0 для 0, інакше 1 + floor(log2(val))
}

template <std::unsigned_integral T>
[[nodiscard]] constexpr bool is_power_of_two(T val) noexcept {
    return std::has_single_bit(val); // Безпечно для 0: повертає false
}

template <std::unsigned_integral T>
[[nodiscard]] constexpr T round_up_allocation_size(T bytes) noexcept {
    return std::bit_ceil(bytes); // Обчислюється під час компіляції (constexpr)
}
