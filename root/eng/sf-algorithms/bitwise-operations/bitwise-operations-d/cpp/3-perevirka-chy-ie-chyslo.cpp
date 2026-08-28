#include <bit>
#include <concepts>

// C++20 стандартна функція перевірки (або прямий побітовий вираз)
template <std::integral T>
[[nodiscard]] constexpr bool is_power_of_two(T x) noexcept {
    if constexpr (std::unsigned_integral<T>) {
        return std::has_single_bit(x);
    } else {
        return (x > 0) && ((x & (x - 1)) == 0);
    }
}
