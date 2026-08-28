#include <cstdint>
#include <bit>
#include <optional>
#include <concepts>

// В C++20 усі операції безпечні, стандартизовані та підтримують constexpr
template <std::unsigned_integral T>
[[nodiscard]] constexpr int safe_clz(T val) noexcept {
    return std::countl_zero(val); // Для нуля повертає std::numeric_limits<T>::digits
}

template <std::unsigned_integral T>
[[nodiscard]] constexpr std::optional<int> safe_ilog2(T val) noexcept {
    if (val == 0) {
        return std::nullopt;
    }
    return std::bit_width(val) - 1; // bit_width обчислює 1 + floor(log2(val))
}

template <std::unsigned_integral T>
[[nodiscard]] constexpr bool is_power_of_two(T val) noexcept {
    return std::has_single_bit(val); // Безпечна перевірка 2ⁿ без розгалужень
}
