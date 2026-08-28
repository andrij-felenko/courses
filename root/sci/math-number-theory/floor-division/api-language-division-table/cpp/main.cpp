#include <cstdint>
#include <limits>
#include <concepts>

// Ідіоматична C++20 перевірка без винятків
template <std::signed_integral T>
[[nodiscard]] constexpr bool is_safe_division(T a, T b) noexcept {
    if (b == 0) return false;
    if (a == std::numeric_limits<T>::min() && b == -1) return false;
    return true;
}
